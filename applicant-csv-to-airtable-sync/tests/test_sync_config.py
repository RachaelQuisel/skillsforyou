from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_config.py"
EXAMPLE = Path(__file__).resolve().parents[1] / "references" / "config.example.json"


def load_module():
    spec = importlib.util.spec_from_file_location("sync_config", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def filled_config() -> dict:
    """The example config with every placeholder replaced.

    These stand-ins are deliberately shorter than a real Airtable id so the leak
    check in test_skill_contract.py keeps flagging only the real thing.
    """
    config = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    config["baseId"] = "appRealBase0001"
    config["automationLogTableId"] = "tblRealLog00001"
    config["automationInventoryTableId"] = "tblRealInv00001"
    config["automationInventoryRecordId"] = "recRealRec00001"
    config["fields"] = {
        key: f"fldReal{index:04d}" for index, key in enumerate(config["fields"], start=1)
    }
    config["tables"] = {
        name: {"tableId": f"tblReal{index:04d}", "viewId": f"viwReal{index:04d}"}
        for index, name in enumerate(config["tables"], start=1)
    }
    return config


class SyncConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def write(self, config: dict) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(config, handle)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def test_requires_a_configuration_path(self) -> None:
        with self.assertRaisesRegex(self.module.ConfigError, "No configuration supplied"):
            self.module.load_config(None)

    def test_rejects_a_missing_file(self) -> None:
        with self.assertRaisesRegex(self.module.ConfigError, "does not exist"):
            self.module.load_config("/nonexistent/applicant-sync-config.json")

    def test_rejects_invalid_json(self) -> None:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        handle.write("{not json")
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        with self.assertRaisesRegex(self.module.ConfigError, "not valid JSON"):
            self.module.load_config(handle.name)

    def test_rejects_the_unedited_example_placeholders(self) -> None:
        path = self.write(json.loads(EXAMPLE.read_text(encoding="utf-8")))
        with self.assertRaisesRegex(self.module.ConfigError, "placeholder"):
            self.module.load_config(path)

    def test_rejects_a_missing_field_id(self) -> None:
        config = filled_config()
        del config["fields"]["runKey"]
        with self.assertRaisesRegex(self.module.ConfigError, "fields.runKey"):
            self.module.load_config(self.write(config))

    def test_rejects_an_identifier_with_the_wrong_prefix(self) -> None:
        config = filled_config()
        config["baseId"] = "tblNotABase0001"
        with self.assertRaisesRegex(self.module.ConfigError, "should start with 'app'"):
            self.module.load_config(self.write(config))

    def test_rejects_a_table_entry_missing_its_view(self) -> None:
        config = filled_config()
        del config["tables"]["Application"]["viewId"]
        with self.assertRaisesRegex(self.module.ConfigError, "Application is missing viewId"):
            self.module.load_config(self.write(config))

    def test_rejects_a_table_placeholder_left_in_place(self) -> None:
        config = filled_config()
        config["tables"]["Applicant"]["tableId"] = "tblXXXXXXXXXXXXXX"
        with self.assertRaisesRegex(self.module.ConfigError, "placeholder for table Applicant"):
            self.module.load_config(self.write(config))

    def test_accepts_a_fully_filled_configuration(self) -> None:
        loaded = self.module.load_config(self.write(filled_config()))
        self.assertEqual(loaded["baseId"], "appRealBase0001")
        self.assertEqual(loaded["writerId"], "applicant-csv-import")
        self.assertIn("runKey", loaded["fields"])

    def test_reads_the_path_from_the_environment(self) -> None:
        path = self.write(filled_config())
        os.environ[self.module.CONFIG_ENV_VAR] = str(path)
        self.addCleanup(os.environ.pop, self.module.CONFIG_ENV_VAR, None)
        self.assertEqual(
            self.module.load_config()["automationLogTableId"], "tblRealLog00001"
        )

    def test_builds_table_and_record_links_from_the_configuration(self) -> None:
        config = self.module.load_config(self.write(filled_config()))
        table_url = self.module.table_link(config, "Application")
        self.assertTrue(table_url.startswith("https://airtable.com/appRealBase0001/"))
        self.assertEqual(
            self.module.table_link(config, "Application", "recSomeRecord"),
            f"{table_url}/recSomeRecord",
        )
        with self.assertRaisesRegex(self.module.ConfigError, "No configured table"):
            self.module.table_link(config, "Nonexistent")


if __name__ == "__main__":
    unittest.main()
