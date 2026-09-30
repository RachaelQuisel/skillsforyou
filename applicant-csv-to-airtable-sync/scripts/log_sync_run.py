#!/usr/bin/env python3
"""Create or update the one Automation Log row for an applicant CSV sync run.

Destination identifiers come from the configuration file described in
``references/config.md``. Nothing about a specific base is hardcoded here.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sync_config import ConfigError, load_config  # noqa: E402


def run_airtable_cli(tool: str, payload: dict[str, Any]) -> dict[str, Any]:
    command = ["airtable-mcp", tool, "--input", "-"]
    last_error = f"Airtable did not complete {tool}."
    for attempt in range(3):
        completed = subprocess.run(
            command,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        if not completed.returncode:
            try:
                result = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                raise RuntimeError("Airtable returned an unreadable response.") from exc
            if not isinstance(result, dict):
                raise RuntimeError("Airtable returned an unexpected response.")
            return result
        last_error = completed.stderr.strip() or last_error
        if attempt < 2:
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(last_error)


def normalize_organizations(values: list[str]) -> list[str]:
    return sorted({value.strip() for value in values if value.strip()}, key=str.casefold)


def build_log_fields(
    config: dict[str, Any],
    *,
    run_key: str,
    outcome: str,
    source_organizations: list[str],
    fields_written: str,
    notes: str,
    reason: str | None,
    duration_ms: int,
    logged_at: str | None = None,
) -> dict[str, Any]:
    ids = config["fields"]
    organizations = normalize_organizations(source_organizations)
    organization_text = ", ".join(organizations) if organizations else "pending source validation"
    organization_note = (
        f"Source organizations: {', '.join(organizations)}."
        if organizations
        else "Source organizations: pending until the CSV is validated."
    )
    return {
        ids["automationName"]: config["automationName"],
        ids["outcome"]: outcome,
        ids["source"]: f"Applicant CSV: {organization_text}",
        ids["runKey"]: run_key,
        ids["reason"]: reason or "",
        ids["fieldsWritten"]: fields_written,
        ids["notes"]: f"{organization_note} {notes}".strip(),
        ids["durationMs"]: max(0, int(duration_ms)),
        ids["loggedAt"]: logged_at
        or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        ids["automationLink"]: [config["automationInventoryRecordId"]],
    }


def _matching_records(
    payload: dict[str, Any], run_key: str, run_key_field_id: str
) -> list[dict[str, Any]]:
    return [
        record
        for record in payload.get("records", [])
        if record.get("cellValuesByFieldId", {}).get(run_key_field_id) == run_key
    ]


def upsert_automation_log(
    config: dict[str, Any],
    run_key: str,
    fields: dict[str, Any],
    *,
    runner: Callable[[str, dict[str, Any]], dict[str, Any]] = run_airtable_cli,
) -> str:
    base_id = config["baseId"]
    table_id = config["automationLogTableId"]
    run_key_field_id = config["fields"]["runKey"]
    logged_at_field_id = config["fields"]["loggedAt"]

    filters = {
        "operator": "and",
        "operands": [{"operator": "=", "operands": [run_key_field_id, run_key]}],
    }
    current = runner(
        "list-records-for-table",
        {
            "baseId": base_id,
            "tableId": table_id,
            "filters": filters,
            "fieldIds": [run_key_field_id],
            "pageSize": 3,
        },
    )
    matches = _matching_records(current, run_key, run_key_field_id)
    if len(matches) > 1:
        raise RuntimeError("Found more than one Automation Log record for the run key.")

    if not matches:
        response = runner(
            "create-records-for-table",
            {"baseId": base_id, "tableId": table_id, "records": [{"fields": fields}]},
        )
    else:
        record_id = str(matches[0]["id"])
        update_fields = dict(fields)
        update_fields.pop(logged_at_field_id, None)
        response = runner(
            "update-records-for-table",
            {
                "baseId": base_id,
                "tableId": table_id,
                "records": [{"id": record_id, "fields": update_fields}],
            },
        )

    records = response.get("records", [])
    if len(records) != 1 or not records[0].get("id"):
        raise RuntimeError("The Automation Log write could not be confirmed.")
    return str(records[0]["id"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to the destination configuration JSON.")
    parser.add_argument("--run-key", required=True)
    parser.add_argument("--outcome", choices=("Succeeded", "Skipped", "Failed"), required=True)
    parser.add_argument("--organization", action="append", default=[])
    parser.add_argument("--fields-written", required=True)
    parser.add_argument("--notes", required=True)
    parser.add_argument("--reason")
    parser.add_argument("--duration-ms", type=int, required=True)
    parser.add_argument("--logged-at")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    fields = build_log_fields(
        config,
        run_key=args.run_key,
        outcome=args.outcome,
        source_organizations=args.organization,
        fields_written=args.fields_written,
        notes=args.notes,
        reason=args.reason,
        duration_ms=args.duration_ms,
        logged_at=args.logged_at,
    )
    record_id = upsert_automation_log(config, args.run_key, fields)
    print(json.dumps({"recordId": record_id, "outcome": args.outcome}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
