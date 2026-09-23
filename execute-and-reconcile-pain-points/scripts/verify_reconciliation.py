#!/usr/bin/env python3
"""Verify a Pain Point update against its frozen before-state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: str) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_records(payload: Any, label: str) -> dict[str, dict[str, Any]]:
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError(f"{label} must be a record array or an object with a records array")

    normalized: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            raise ValueError(f"{label} record {index} must contain a string id")
        record_id = record["id"]
        if record_id in normalized:
            raise ValueError(f"{label} contains duplicate record id {record_id}")
        fields = record.get("fields", record.get("cellValuesByFieldId"))
        if not isinstance(fields, dict):
            raise ValueError(
                f"{label} record {record_id} must contain fields or cellValuesByFieldId"
            )
        normalized[record_id] = fields
    return normalized


def normalize_value(value: Any, field_id: str, newline_fields: set[str]) -> Any:
    if field_id in newline_fields and isinstance(value, str):
        return value.rstrip("\r\n")
    return value


def normalize_field_ids(manifest_payload: dict[str, Any], key: str) -> set[str]:
    value = manifest_payload.get(key, [])
    if not isinstance(value, list) or any(
        not isinstance(field_id, str) or not field_id for field_id in value
    ):
        raise ValueError(f"manifest {key} must be an array of non-empty strings")
    return set(value)


def audit(before_payload: Any, after_payload: Any, manifest_payload: Any) -> dict[str, Any]:
    if not isinstance(manifest_payload, dict):
        raise ValueError("manifest must be an object")
    before = normalize_records(before_payload, "before")
    after = normalize_records(after_payload, "after")
    manifest = normalize_records(manifest_payload, "manifest")

    ignored = normalize_field_ids(manifest_payload, "ignoredFieldIds")
    newline_fields = normalize_field_ids(
        manifest_payload, "allowTrailingNewlineFieldIds"
    )
    append_fields = normalize_field_ids(manifest_payload, "appendFieldIds")
    intended_fields = {
        field_id for record_fields in manifest.values() for field_id in record_fields
    }
    if not intended_fields:
        raise ValueError("manifest must contain at least one intended field")
    ignored_intended_fields = sorted(ignored & intended_fields)
    if ignored_intended_fields:
        raise ValueError(
            "manifest fields cannot be both intended and ignored: "
            + ", ".join(ignored_intended_fields)
        )
    errors: list[dict[str, Any]] = []
    intended_checks = 0

    unexpected_before_ids = sorted(set(before) - set(manifest))
    unexpected_after_ids = sorted(set(after) - set(manifest))
    missing_before_ids = sorted(set(manifest) - set(before))
    missing_after_ids = sorted(set(manifest) - set(after))

    for record_id in unexpected_before_ids:
        errors.append({"type": "unmanifested_before_record", "recordId": record_id})
    for record_id in unexpected_after_ids:
        errors.append({"type": "unmanifested_after_record", "recordId": record_id})
    for record_id in missing_before_ids:
        errors.append({"type": "missing_before_record", "recordId": record_id})
    for record_id in missing_after_ids:
        errors.append({"type": "missing_after_record", "recordId": record_id})

    for record_id in sorted(set(manifest) & set(before) & set(after)):
        before_fields = before[record_id]
        after_fields = after[record_id]
        expected_fields = manifest[record_id]
        all_field_ids = set(before_fields) | set(after_fields) | set(expected_fields)

        for field_id in sorted(all_field_ids - ignored):
            before_value = normalize_value(before_fields.get(field_id), field_id, newline_fields)
            after_value = normalize_value(after_fields.get(field_id), field_id, newline_fields)

            if field_id in expected_fields:
                intended_checks += 1
                expected_value = normalize_value(
                    expected_fields[field_id], field_id, newline_fields
                )
                raw_before_value = before_fields.get(field_id)
                raw_after_value = after_fields.get(field_id)
                if (
                    field_id in append_fields
                    and isinstance(raw_before_value, str)
                    and raw_before_value
                ):
                    if (
                        not isinstance(raw_after_value, str)
                        or not raw_after_value.startswith(raw_before_value)
                    ):
                        errors.append(
                            {
                                "type": "append_history_lost",
                                "recordId": record_id,
                                "fieldId": field_id,
                            }
                        )
                    elif not raw_after_value.startswith(raw_before_value + "\n\n"):
                        errors.append(
                            {
                                "type": "append_separator_missing",
                                "recordId": record_id,
                                "fieldId": field_id,
                            }
                        )
                if after_value != expected_value:
                    errors.append(
                        {
                            "type": "missing_expected_change",
                            "recordId": record_id,
                            "fieldId": field_id,
                            "expected": expected_value,
                            "actual": after_value,
                        }
                    )
            elif after_value != before_value:
                errors.append(
                    {
                        "type": "unintended_change",
                        "recordId": record_id,
                        "fieldId": field_id,
                        "before": before_value,
                        "after": after_value,
                    }
                )

    return {
        "result": "PASS" if not errors else "FAIL",
        "recordsChecked": len(set(manifest) & set(before) & set(after)),
        "intendedFieldsChecked": intended_checks,
        "ignoredFieldIds": sorted(ignored),
        "appendFieldIds": sorted(append_fields),
        "errors": errors,
    }


def self_test() -> None:
    before = {
        "records": [
            {
                "id": "rec1",
                "fields": {"status": "New", "updates": "older", "notes": "keep"},
            }
        ]
    }
    after_ok = {
        "records": [
            {
                "id": "rec1",
                "fields": {
                    "status": "In Progress",
                    "updates": "older\n\nverified\n",
                    "notes": "keep",
                },
            }
        ]
    }
    manifest = {
        "allowTrailingNewlineFieldIds": ["updates"],
        "appendFieldIds": ["updates"],
        "records": [
            {
                "id": "rec1",
                "fields": {"status": "In Progress", "updates": "older\n\nverified"},
            }
        ],
    }
    assert audit(before, after_ok, manifest)["result"] == "PASS"

    after_bad = json.loads(json.dumps(after_ok))
    after_bad["records"][0]["fields"]["notes"] = "changed"
    bad_result = audit(before, after_bad, manifest)
    assert bad_result["result"] == "FAIL"
    assert bad_result["errors"][0]["type"] == "unintended_change"

    after_history_lost = json.loads(json.dumps(after_ok))
    after_history_lost["records"][0]["fields"]["updates"] = "verified"
    history_result = audit(before, after_history_lost, manifest)
    assert history_result["result"] == "FAIL"
    assert any(error["type"] == "append_history_lost" for error in history_result["errors"])

    missing_result = audit(before, {"records": []}, manifest)
    assert missing_result["result"] == "FAIL"
    assert any(error["type"] == "missing_after_record" for error in missing_result["errors"])

    ignored_intended_manifest = json.loads(json.dumps(manifest))
    ignored_intended_manifest["ignoredFieldIds"] = ["status"]
    try:
        audit(before, after_ok, ignored_intended_manifest)
    except ValueError:
        pass
    else:
        raise AssertionError("an intended field cannot also be ignored")

    empty_fields_manifest = {
        "records": [{"id": "rec1", "fields": {}}],
    }
    try:
        audit(before, before, empty_fields_manifest)
    except ValueError:
        pass
    else:
        raise AssertionError("a manifest must contain at least one intended field")

    after_bad_separator = json.loads(json.dumps(after_ok))
    after_bad_separator["records"][0]["fields"]["updates"] = "olderverified"
    bad_separator_manifest = json.loads(json.dumps(manifest))
    bad_separator_manifest["records"][0]["fields"]["updates"] = "olderverified"
    separator_result = audit(before, after_bad_separator, bad_separator_manifest)
    assert separator_result["result"] == "FAIL"
    assert any(
        error["type"] == "append_separator_missing"
        for error in separator_result["errors"]
    )
    print("PASS: 7 self-test cases")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", help="Frozen before-state JSON")
    parser.add_argument("--after", help="Post-write JSON")
    parser.add_argument("--manifest", help="Exact intended-write manifest JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if not all((args.before, args.after, args.manifest)):
        print("ERROR: --before, --after, and --manifest are required", file=sys.stderr)
        return 2
    try:
        result = audit(
            load_json(args.before), load_json(args.after), load_json(args.manifest)
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
