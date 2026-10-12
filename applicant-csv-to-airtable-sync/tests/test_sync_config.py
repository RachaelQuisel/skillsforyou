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

    def filled_gol_config(self) -> dict:
        """The example with only the still-unknown ids replaced."""
        config = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        config["automationInventoryRecordId"] = "recRealRec00001"
        config["fields"] = {
            key: f"fldReal{index:04d}" for index, key in enumerate(config["fields"], start=1)
        }
        for entry in config["tables"].values():
            entry["viewId"] = "viwRealView00001"
        return config

    def test_maps_binti_csv_headers_onto_gol_base_fields(self) -> None:
        self.assertEqual(
            self.module.application_field_for_csv_header("Binti application id"),
            "Binti ID",
        )
        self.assertEqual(
            self.module.application_field_for_csv_header("\ufeffBinti application id"),
            "Binti ID",
        )
        self.assertEqual(self.module.application_field_for_csv_header("Rfa id"), "RFA ID")
        self.assertEqual(self.module.application_field_for_csv_header("\ufeffRfa id"), "RFA ID")
        self.assertIsNone(
            self.module.application_field_for_csv_header("Applicant external identifier")
        )
        self.assertTrue(self.module.header_is_person_id("Binti Person ID"))
        self.assertTrue(self.module.header_is_person_id("Person ID"))
        for header in (
            "Applicant external identifier",
            "Co-applicant external identifier",
            "Applicant email",
            "Applicant phone number",
            "Binti application id",
            "Rfa id",
        ):
            self.assertFalse(self.module.header_is_person_id(header), header)
        self.assertEqual(
            self.module.application_field_id_for_csv_header("\ufeffBinti application id"),
            "fldsxEB5mSLl3MBK6",
        )
        self.assertEqual(
            self.module.application_field_id_for_csv_header("Rfa id"),
            "fldR9l7Jjm6Gr9yJV",
        )
        self.assertEqual(
            self.module.application_field_for_csv_header("Status"),
            "Case Status",
        )
        self.assertEqual(
            self.module.application_field_id_for_csv_header("Status"),
            "fld3HrhY9xh9EWTso",
        )

    def test_mapped_field_name_is_rejected_as_an_api_key(self) -> None:
        for item in self.module.GOL_FIELDS:
            self.assertRegex(item["fieldId"], r"^fld[A-Za-z0-9]{14}$")
            self.assertNotRegex(item["label"], r"^fld[A-Za-z0-9]{14}$")
            self.assertNotEqual(item["label"], item["fieldId"])
        for item in self.module.UNRESOLVED_FIELDS:
            self.assertNotIn("fieldId", item)
        binti = self.module.field_id("Application", "Binti ID")
        rfa = self.module.field_id("Application", "RFA ID")
        with self.assertRaisesRegex(self.module.ConfigError, "field ID, not a field name"):
            self.module.build_upsert("Application", ["Binti ID"], {"Binti ID": "9000001"})
        with self.assertRaisesRegex(self.module.ConfigError, "field ID, not a field name"):
            self.module.filter_by_formula({"RFA ID": "RFA-100001"})
        with self.assertRaisesRegex(self.module.ConfigError, "not upsert keys"):
            self.module.build_upsert(
                "Application",
                [self.module.MIGRATION_RECID_FIELD_ID],
                {self.module.MIGRATION_RECID_FIELD_ID: "recOld"},
            )
        with self.assertRaisesRegex(self.module.ConfigError, "not upsert keys"):
            lookup = self.module.field_id("Applicant", "RFA ID (from Applications)")
            self.module.build_upsert("Applicant", [lookup], {lookup: "RFA-1"})
        body = self.module.build_upsert("Application", [binti], {binti: "9000001", rfa: "RFA-100001"})
        self.assertEqual(body["performUpsert"]["fieldsToMergeOn"], [binti])
        self.assertTrue(body["returnFieldsByFieldId"])
        self.assertEqual(set(body["records"][0]["fields"]), {binti, rfa})
        self.assertNotIn("Binti ID", json.dumps(body["performUpsert"]))
        formula = body and self.module.filter_by_formula({binti: "9000001"})
        self.assertEqual(formula, "{fldsxEB5mSLl3MBK6}='9000001'")
        self.assertNotIn("Binti ID", formula)

    def test_application_lookups_use_separate_field_id_formulas(self) -> None:
        requests = self.module.application_match_requests("9000001", "RFA-100001")
        self.assertEqual(len(requests), 2)
        for request in requests:
            self.assertTrue(request["returnFieldsByFieldId"])
            self.assertNotIn("AND(", request["filterByFormula"])
            self.assertNotIn("Binti ID", request["filterByFormula"])
            self.assertNotIn("RFA ID", request["filterByFormula"])
        self.assertIn("{fldR9l7Jjm6Gr9yJV}", requests[0]["filterByFormula"])
        self.assertNotIn("{fldsxEB5mSLl3MBK6}", requests[0]["filterByFormula"])
        self.assertIn("{fldsxEB5mSLl3MBK6}", requests[1]["filterByFormula"])
        self.assertNotIn("{fldR9l7Jjm6Gr9yJV}", requests[1]["filterByFormula"])
        blank_rfa = self.module.application_match_requests("9000001", "  ")
        self.assertEqual(len(blank_rfa), 1)
        self.assertIn("{fldsxEB5mSLl3MBK6}", blank_rfa[0]["filterByFormula"])
        self.assertNotIn("fldR9l7Jjm6Gr9yJV", blank_rfa[0]["filterByFormula"])
        blank_binti = self.module.application_match_requests("  ", "RFA-100001")
        self.assertEqual(len(blank_binti), 1)
        self.assertIn("{fldR9l7Jjm6Gr9yJV}", blank_binti[0]["filterByFormula"])
        self.assertNotIn("fldsxEB5mSLl3MBK6", blank_binti[0]["filterByFormula"])
        self.assertIsNone(self.module.applicant_match_request(None))
        self.assertIsNone(self.module.applicant_match_request("  "))
        person = self.module.applicant_match_request("person-1")
        self.assertEqual(person["filterByFormula"], "{flddz0UmEcHGNreOF}='person-1'")
        self.assertEqual(
            self.module.link_fields("Application", "Case Task", ["recTask1"]),
            {"fldFxMTIjCttt2vC9": ["recTask1"]},
        )
        self.assertEqual(
            self.module.link_fields("Historical", "Application", ["recApp1"]),
            {"fldrhq6h7Y5kUjRBe": ["recApp1"]},
        )

    def test_historical_event_key_uses_record_type_and_date(self) -> None:
        key = self.module.historical_event_key(
            " recApp1 ", " Application Signed ", " 2024-01-02 "
        )
        self.assertEqual(key, ("recApp1", "Application Signed", "2024-01-02"))
        self.assertEqual(
            key,
            self.module.historical_event_key("recApp1", "Application Signed", "2024-01-02"),
        )
        self.assertNotIn("binti:", key)
        self.assertNotEqual(key[0], "binti:9000001:application-signed")
        with self.assertRaisesRegex(self.module.ConfigError, "Historical event key"):
            self.module.historical_event_key("recApp1", "  ", "2024-01-02")
        unresolved = {
            item["label"]: item
            for item in self.module.UNRESOLVED_FIELDS
            if item["table"] == "Historical"
        }
        for label in ("Date", "Type", "Migration Key"):
            self.assertIn(label, unresolved)
            self.assertNotIn("fieldId", unresolved[label])

    def test_example_match_keys_are_the_gol_base_contract(self) -> None:
        example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(example["baseId"], self.module.GOL_BASE_ID)
        self.assertEqual(example["matchKeys"], self.module.gol_match_keys())
        self.assertEqual(list(example["writeOrder"]), list(self.module.WRITE_ORDER))
        self.assertEqual(
            example["tables"]["Assigned Tasks"]["tableId"],
            self.module.TABLE_IDS["Assigned Tasks"],
        )

    def test_accepts_a_filled_gol_base_configuration(self) -> None:
        loaded = self.module.load_config(self.write(self.filled_gol_config()))
        self.assertEqual(loaded["baseId"], self.module.GOL_BASE_ID)
        self.assertEqual(loaded["tables"]["Application"]["tableId"], "tblle86w7gTHmBsDS")
        self.assertIn("Assigned Tasks", loaded["tables"])

    def test_rejects_the_retired_gol_erp_base(self) -> None:
        config = self.filled_gol_config()
        config["baseId"] = self.module.RETIRED_ERP_BASE_ID
        with self.assertRaisesRegex(self.module.ConfigError, "retired GOL ERP"):
            self.module.load_config(self.write(config))

    def test_rejects_the_old_case_task_table_name(self) -> None:
        config = filled_config()
        config["tables"]["Case Task"] = {
            "tableId": "tblOldCaseTask01",
            "viewId": "viwOldCaseTask01",
        }
        with self.assertRaisesRegex(self.module.ConfigError, "Assigned Tasks"):
            self.module.load_config(self.write(config))

    def test_rejects_a_gol_base_config_with_the_wrong_application_table(self) -> None:
        config = self.filled_gol_config()
        config["tables"]["Application"]["tableId"] = "tblNotApplication1"
        with self.assertRaisesRegex(self.module.ConfigError, "table Application must be"):
            self.module.load_config(self.write(config))

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
