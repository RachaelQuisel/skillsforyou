from __future__ import annotations

import importlib.util
import tempfile
import unittest
import copy
from unittest.mock import patch
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "attach_log_documents.py"

# Fixture identifiers are deliberately shorter than a real Airtable id, so the
# leak check in test_skill_contract.py keeps flagging only the real thing.


def load_module():
    spec = importlib.util.spec_from_file_location("attach_log_documents", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AttachLogDocumentsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_only_accepts_documents_inside_client_safe_docs_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            root.mkdir()
            public = root / "change-report.md"
            public.write_text("aggregate only", encoding="utf-8")
            private = Path(tmp) / "record-manifest.private.csv"
            private.write_text("private", encoding="utf-8")
            misplaced_private = root / "record-manifest.private.csv"
            misplaced_private.write_text("private", encoding="utf-8")

            self.assertEqual(
                self.module.validate_document_paths([public], root),
                [public.resolve()],
            )
            with self.assertRaisesRegex(ValueError, "client-safe docs root"):
                self.module.validate_document_paths([private], root)
            with self.assertRaisesRegex(ValueError, "private artifact"):
                self.module.validate_document_paths([misplaced_private], root)

    def test_resolves_exactly_one_log_record_for_the_stable_run_key(self) -> None:
        run_key = "applicant-csv-to-airtable-sync:2026-09-10T04:40:30Z"
        payload = {
            "records": [
                {
                    "id": "recExample",
                    "cellValuesByFieldId": {
                        "fldRunKey": run_key,
                        "fldDocsField": [{"filename": "existing.md"}],
                    },
                }
            ]
        }

        record_id, filenames = self.module.resolve_log_record(
            payload,
            run_key,
            "fldRunKey",
            "fldDocsField",
        )

        self.assertEqual(record_id, "recExample")
        self.assertEqual(filenames, {"existing.md"})

    def test_rejects_missing_or_duplicate_log_records(self) -> None:
        run_key = "applicant-csv-to-airtable-sync:run"
        with self.assertRaisesRegex(RuntimeError, "exactly one"):
            self.module.resolve_log_record(
                {"records": []}, run_key, "fldRunKey", "fldDocs"
            )
        duplicate = {
            "records": [
                {"id": "recOne", "cellValuesByFieldId": {"fldRunKey": run_key}},
                {"id": "recTwo", "cellValuesByFieldId": {"fldRunKey": run_key}},
            ]
        }
        with self.assertRaisesRegex(RuntimeError, "exactly one"):
            self.module.resolve_log_record(
                duplicate, run_key, "fldRunKey", "fldDocs"
            )

    def test_same_filename_and_size_do_not_prove_matching_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            document = Path(tmp) / "report.md"
            document.write_bytes(b"new text")
            attachment = {"id": "attOld", "filename": document.name, "size": 8, "url": "old"}
            self.assertIsNone(self.module.exact_attachment([attachment], document, lambda url: b"old text"))
            self.assertEqual(self.module.exact_attachment([attachment], document, lambda url: b"new text"), attachment)

    def test_refreshes_stale_same_name_contents_then_keeps_one_verified_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            document = Path(tmp) / "report.md"
            document.write_bytes(b"new text")
            docs = [{"id": "attOld", "filename": document.name, "size": 8, "url": "old"}]
            content = {"old": b"old text", "new": b"new text"}
            events = []
            def fetch(*args):
                return {"records": [{"id": "recRun", "cellValuesByFieldId": {"key": "run", "docs": copy.deepcopy(docs)}}]}
            def upload(*args):
                events.append("upload")
                docs.append({"id": "attNew", "filename": document.name, "size": 8, "url": "new"})
            def cli(*args):
                events.append("trim")
                docs[:] = [item for item in docs if item["id"] == "attNew"]
                return {}
            with patch.object(self.module, "fetch_log_records", fetch), patch.object(self.module, "load_airtable_token", return_value="mock"), patch.object(self.module, "run_airtable_cli", cli):
                result = self.module.attach_documents("run", [document], "base", "table", "key", "docs", None, upload, content.__getitem__)
                second = self.module.attach_documents("run", [document], "base", "table", "key", "docs", None, upload, content.__getitem__)
            self.assertEqual(events, ["upload", "trim"])
            self.assertEqual(result["uploaded"], 1)
            self.assertEqual(result["removed"], 1)
            self.assertEqual(second["uploaded"], 0)
            self.assertEqual(second["verified"], 1)
            self.assertEqual(len(docs), 1)

    def test_bad_uploaded_contents_do_not_remove_the_previous_attachment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            document = Path(tmp) / "report.md"
            document.write_bytes(b"new text")
            docs = [{"id": "attOld", "filename": document.name, "size": 8, "url": "old"}]
            def fetch(*args):
                return {"records": [{"id": "recRun", "cellValuesByFieldId": {"key": "run", "docs": copy.deepcopy(docs)}}]}
            def upload(*args):docs.append({"id": "attBad", "filename": document.name, "size": 8, "url": "bad"})
            with patch.object(self.module, "fetch_log_records", fetch), patch.object(self.module, "load_airtable_token", return_value="mock"), patch.object(self.module, "run_airtable_cli") as cli:
                with self.assertRaisesRegex(RuntimeError, "contents could not be verified"):
                    self.module.attach_documents("run", [document], "base", "table", "key", "docs", None, upload, lambda url: b"bad text")
                cli.assert_not_called()
            self.assertIn("attOld", {item["id"] for item in docs})

    def test_missing_size_or_url_is_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            document = Path(tmp) / "report.md"
            document.write_bytes(b"new text")
            for attachment in [{"id": "att", "filename": document.name}, {"id": "att", "filename": document.name, "size": 8}]:
                self.assertIsNone(self.module.exact_attachment([attachment], document, lambda url: b"new text"))


if __name__ == "__main__":
    unittest.main()
