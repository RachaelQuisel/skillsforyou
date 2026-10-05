#!/usr/bin/env python3
"""Load the Airtable destination configuration for the applicant CSV sync.

The live destination is GoL Base. The retired GOL ERP base ID is rejected.
View IDs and Automation Log field IDs still come from the configuration file
described in ``references/config.md``. Point the scripts at that file with
``--config`` or the ``APPLICANT_SYNC_CONFIG`` environment variable.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


CONFIG_ENV_VAR = "APPLICANT_SYNC_CONFIG"
PLACEHOLDER = re.compile(r"X{4,}")
REQUIRED_FIELD_KEYS = (
    "automationName",
    "outcome",
    "source",
    "runKey",
    "reason",
    "fieldsWritten",
    "notes",
    "durationMs",
    "loggedAt",
    "automationLink",
    "clientDocuments",
)
ID_PREFIXES = {
    "baseId": "app",
    "automationLogTableId": "tbl",
    "automationInventoryTableId": "tbl",
    "automationInventoryRecordId": "rec",
}

# Live destination. appp6pbBbaxuOLu2v is GOL ERP, the pre-migration base.
GOL_BASE_NAME = "GoL Base"
GOL_BASE_ID = "appcxLcvRF7dWQOHH"
RETIRED_ERP_BASE_NAME = "GOL ERP"
RETIRED_ERP_BASE_ID = "appp6pbBbaxuOLu2v"

WRITE_ORDER = (
    "Application",
    "Applicant",
    "Historical",
    "Team Assignment",
    "Assigned Tasks",
)

TABLE_IDS = {
    "Application": "tblle86w7gTHmBsDS",
    "Applicant": "tblZsYxi9G7MVI7p5",
    "Historical": "tbl3VYr0NXusmTu7X",
    "Team Assignment": "tblmNxsRPLxsxSNbr",
    "Assigned Tasks": "tblVB0TYikSrpf2tg",
    "Automation Log": "tblprCx6rMOrVNhrf",
    "Automation Inventory": "tblIrEObjqmmqzAHb",
}

# Staff is read for a unique person match. Its field IDs were not in the schema summary.
STAFF_TABLE_ID = "tbltuqSEdJuKk6763"

# label is the current Airtable name. API calls use fieldId only.
# csvHeader, when present, is the Binti export header and is not an Airtable name.
GOL_FIELDS: tuple[dict[str, str], ...] = (
    {"table": "Application", "label": "Binti ID", "fieldId": "fldsxEB5mSLl3MBK6", "role": "upsert", "csvHeader": "Binti application id"},
    {"table": "Application", "label": "RFA ID", "fieldId": "fldR9l7Jjm6Gr9yJV", "role": "upsert", "csvHeader": "Rfa id"},
    {"table": "Application", "label": "Case Status", "fieldId": "fld3HrhY9xh9EWTso", "role": "write", "csvHeader": "Status"},
    {"table": "Application", "label": "Applicants", "fieldId": "fldITF9OcRYSU952a", "role": "link"},
    {"table": "Application", "label": "Assignment", "fieldId": "fldw87HpCuFHjUdiQ", "role": "link"},
    {"table": "Application", "label": "Events", "fieldId": "fldTn1SLNUBnELbUT", "role": "link"},
    {"table": "Application", "label": "Case Task", "fieldId": "fldFxMTIjCttt2vC9", "role": "link"},
    {"table": "Application", "label": "GOL ERP Base RecID", "fieldId": "fldtVbqKPooJGhu5A", "role": "migration-only"},
    {"table": "Applicant", "label": "Binti Person ID", "fieldId": "flddz0UmEcHGNreOF", "role": "upsert"},
    {"table": "Applicant", "label": "RFA ID (from Applications)", "fieldId": "fldnNRWueleJKZWtV", "role": "lookup"},
    {"table": "Historical", "label": "Application", "fieldId": "fldrhq6h7Y5kUjRBe", "role": "link"},
)

MIGRATION_RECID_FIELD = "GOL ERP Base RecID"
MIGRATION_RECID_FIELD_ID = "fldtVbqKPooJGhu5A"

PERSON_ID_WHEN = (
    "Only when the CSV or the reviewed person map supplies a person ID. "
    "Do not use Applicant external identifier, phone, or email."
)
PERSON_ID_HEADERS = frozenset({"binti person id", "person id"})
FIELD_ID_PATTERN = re.compile(r"^fld[A-Za-z0-9]{14}$")
NOT_WRITTEN_ROLES = frozenset({"lookup", "migration-only"})

# The schema summary names these fields and does not include their IDs.
# Nothing here is guessed.
UNRESOLVED_FIELDS: tuple[dict[str, str], ...] = (
    {"table": "Application", "label": "Client Type", "reason": "Organization mapping writes Client Type. The summary names the field and has no field ID."},
    {"table": "Team Assignment", "label": "Staff Member", "reason": "A verified staff link is written here. The summary names Staff Member and has no field ID."},
    {"table": "Historical", "label": "Date", "reason": "A renewal status-change event needs its date. The summary names Date and has no field ID."},
    {"table": "Historical", "label": "Type", "reason": "A renewal status-change event needs its type. The summary names Type and has no field ID."},
    {"table": "Assigned Tasks", "label": "Application", "reason": "An Assigned Tasks row links back to Application. The summary names Application and has no field ID."},
    {"table": "Applicant", "label": "Name", "reason": "Exact name evidence reads the primary Name field. The summary has no field ID."},
    {"table": "Staff", "label": "Name", "reason": "Staff matching reads the primary Name field. The summary has no field ID."},
    {"table": "Automation Log", "label": "Automation Name", "configKey": "automationName", "reason": "The log helper writes this field. The summary names it and has no field ID."},
    {"table": "Automation Log", "label": "Outcome", "configKey": "outcome", "reason": "The log helper writes this field. The summary names it and has no field ID."},
    {"table": "Automation Log", "label": "Fields Written", "configKey": "fieldsWritten", "reason": "The log helper writes this field. The summary names it and has no field ID."},
    {"table": "Automation Log", "label": "Notes", "configKey": "notes", "reason": "The log helper writes this field. The summary names it and has no field ID."},
    {"table": "Automation Log", "label": "Run Duration (ms)", "configKey": "durationMs", "reason": "The log helper writes this field. The summary names it and has no field ID."},
    {"table": "Automation Log", "label": "Logged At", "configKey": "loggedAt", "reason": "The log helper writes this field. The summary names it and has no field ID."},
    {"table": "Automation Log", "label": "Automation", "configKey": "automationLink", "reason": "The log helper writes this link. The summary names Automation and has no field ID."},
    {"table": "Automation Log", "label": "run key", "configKey": "runKey", "reason": "The log helper matches on this value. The summary has no Run Key field."},
    {"table": "Automation Log", "label": "client documents", "configKey": "clientDocuments", "reason": "The attachment helper writes this field. The summary has no matching field. Diff Doc was not assumed."},
    {"table": "Automation Log", "label": "source", "configKey": "source", "reason": "The log helper writes a source note. Source Table was not confirmed as this field."},
    {"table": "Automation Log", "label": "reason", "configKey": "reason", "reason": "The log helper writes a reason. Skip Reason was not confirmed as this field."},
)

DOCUMENTED_AIRTABLE_IDS = frozenset(
    {
        GOL_BASE_ID,
        RETIRED_ERP_BASE_ID,
        STAFF_TABLE_ID,
        *TABLE_IDS.values(),
        *(item["fieldId"] for item in GOL_FIELDS),
    }
)


def field_catalog() -> list[dict[str, str]]:
    """JSON-ready copy of the live field IDs. Labels are not API keys."""
    return [dict(item) for item in GOL_FIELDS]


def field_id(table: str, label: str) -> str:
    """Resolve a documented label to its field ID. Labels never go to the API."""
    for item in GOL_FIELDS:
        if item["table"] == table and item["label"] == label:
            return item["fieldId"]
    raise ConfigError(f"No field ID is recorded for {table} {label}.")


def gol_match_keys() -> dict[str, list[dict[str, str]]]:
    """Upsert keys. fieldId is what Airtable receives. label is the current name."""
    grouped: dict[str, list[dict[str, str]]] = {"Application": [], "Applicant": []}
    for item in GOL_FIELDS:
        if item["role"] != "upsert":
            continue
        entry = {"label": item["label"], "fieldId": item["fieldId"]}
        if "csvHeader" in item:
            entry["csvHeader"] = item["csvHeader"]
        if item["table"] == "Applicant":
            entry["when"] = PERSON_ID_WHEN
        grouped[item["table"]].append(entry)
    return grouped


def _require_field_id(value: str) -> str:
    if not isinstance(value, str) or FIELD_ID_PATTERN.fullmatch(value) is None:
        raise ConfigError(
            f"Airtable field reference {value!r} must be a field ID, not a field name."
        )
    return value


def upsert_field_ids(table: str) -> list[str]:
    return [
        item["fieldId"]
        for item in GOL_FIELDS
        if item["table"] == table and item["role"] == "upsert"
    ]


def filter_by_formula(matches: dict[str, str]) -> str:
    """Build filterByFormula with {fieldId} keys. Field names are rejected."""
    if not matches:
        raise ConfigError("filterByFormula needs at least one field ID.")
    parts: list[str] = []
    for field, raw_value in matches.items():
        _require_field_id(field)
        value = str(raw_value).replace("\\", "\\\\").replace("'", "\\'")
        parts.append(f"{{{field}}}='{value}'")
    if len(parts) == 1:
        return parts[0]
    return "AND(" + ",".join(parts) + ")"


def build_list_request(table: str, formula: str, field_ids: list[str]) -> dict[str, Any]:
    """Read records by field ID. returnFieldsByFieldId keeps the response keyed the same way."""
    if table not in TABLE_IDS:
        raise ConfigError(f"No GoL Base table ID is recorded for {table}.")
    for ref in re.findall(r"\{([^{}]+)\}", formula):
        _require_field_id(ref)
    if not re.findall(r"\{([^{}]+)\}", formula):
        raise ConfigError("filterByFormula must reference field IDs as {fld...}.")
    return {
        "baseId": GOL_BASE_ID,
        "tableId": TABLE_IDS[table],
        "returnFieldsByFieldId": True,
        "filterByFormula": formula,
        "fields": [_require_field_id(field) for field in field_ids],
    }


def build_upsert(
    table: str,
    fields_to_merge_on: list[str],
    fields: dict[str, Any],
) -> dict[str, Any]:
    """Upsert one record. fieldsToMergeOn and field keys are field IDs."""
    if table not in TABLE_IDS:
        raise ConfigError(f"No GoL Base table ID is recorded for {table}.")
    allowed = set(upsert_field_ids(table))
    if not fields_to_merge_on:
        raise ConfigError(f"{table} upsert needs at least one field ID in fieldsToMergeOn.")
    merge_ids = [_require_field_id(field) for field in fields_to_merge_on]
    if any(field not in allowed for field in merge_ids):
        raise ConfigError(
            f"{table} fieldsToMergeOn must be upsert field IDs. "
            "Lookup fields and GOL ERP Base RecID are not upsert keys."
        )
    known = {item["fieldId"]: item for item in GOL_FIELDS if item["table"] == table}
    cleaned: dict[str, Any] = {}
    for key, value in fields.items():
        field = _require_field_id(key)
        spec = known.get(field)
        if spec is None:
            raise ConfigError(f"{field} is not a known {table} field ID.")
        if spec["role"] in NOT_WRITTEN_ROLES:
            raise ConfigError(f"{spec['label']} ({field}) is not written by this sync.")
        cleaned[field] = value
    for field in merge_ids:
        if field not in cleaned:
            raise ConfigError(f"Upsert fields are missing the merge field ID {field}.")
    return {
        "baseId": GOL_BASE_ID,
        "tableId": TABLE_IDS[table],
        "returnFieldsByFieldId": True,
        "performUpsert": {"fieldsToMergeOn": merge_ids},
        "records": [{"fields": cleaned}],
    }


def application_match_requests(binti_id: str, rfa_id: str) -> list[dict[str, Any]]:
    """Look up each Application key on its own. A blank RFA is not part of the formula."""
    binti_field = field_id("Application", "Binti ID")
    rfa_field = field_id("Application", "RFA ID")
    requests: list[dict[str, Any]] = []
    if binti_id.strip():
        requests.append(
            build_list_request(
                "Application",
                filter_by_formula({binti_field: binti_id.strip()}),
                [binti_field, rfa_field],
            )
        )
    if rfa_id.strip():
        requests.append(
            build_list_request(
                "Application",
                filter_by_formula({rfa_field: rfa_id.strip()}),
                [binti_field, rfa_field],
            )
        )
    return requests


def applicant_match_request(person_id: str | None) -> dict[str, Any] | None:
    """Match Applicant on Binti Person ID only. No person ID means no Applicant upsert."""
    if person_id is None or not str(person_id).strip():
        return None
    person_field = field_id("Applicant", "Binti Person ID")
    return build_list_request(
        "Applicant",
        filter_by_formula({person_field: str(person_id).strip()}),
        [person_field],
    )


def link_fields(table: str, label: str, record_ids: list[str]) -> dict[str, list[str]]:
    """Linked-record payload. The key is the field ID and the values are record IDs."""
    return {field_id(table, label): list(record_ids)}


def normalize_csv_header(header: str) -> str:
    """Drop a leading BOM. GOL ERP stored one copy of the application id with U+FEFF."""
    return header.lstrip("\ufeff").strip()


def _application_field_for_csv_header(header: str) -> dict[str, str] | None:
    cleaned = normalize_csv_header(header)
    for item in GOL_FIELDS:
        if item["table"] == "Application" and item.get("csvHeader") == cleaned:
            return item
    return None


def application_field_for_csv_header(header: str) -> str | None:
    """Map a Binti CSV header to the current Application field label."""
    item = _application_field_for_csv_header(header)
    return None if item is None else item["label"]


def application_field_id_for_csv_header(header: str) -> str | None:
    """Map a Binti CSV header to the Application field ID used on the API."""
    item = _application_field_for_csv_header(header)
    return None if item is None else item["fieldId"]


def header_is_person_id(header: str) -> bool:
    """True when this CSV header is a Binti person key, not a contact or external id."""
    return normalize_csv_header(header).casefold() in PERSON_ID_HEADERS


class ConfigError(RuntimeError):
    """The configuration is missing, unreadable, or still holds placeholders."""


def resolve_config_path(explicit: str | Path | None = None) -> Path:
    candidate = explicit or os.environ.get(CONFIG_ENV_VAR)
    if not candidate:
        raise ConfigError(
            "No configuration supplied. Pass --config <path> or set "
            f"{CONFIG_ENV_VAR} to a copy of references/config.example.json."
        )
    path = Path(candidate).expanduser()
    if not path.is_file():
        raise ConfigError(f"Configuration file does not exist: {path}")
    return path


def _validate_gol_destination(config: dict[str, Any]) -> None:
    if config.get("baseName") != GOL_BASE_NAME:
        raise ConfigError(f"GoL Base configuration baseName must be {GOL_BASE_NAME!r}.")
    tables = config.get("tables", {})
    for name in WRITE_ORDER:
        entry = tables.get(name)
        if not isinstance(entry, dict) or entry.get("tableId") != TABLE_IDS[name]:
            raise ConfigError(f"GoL Base table {name} must be {TABLE_IDS[name]}.")
    log_entry = tables.get("Automation Log", {})
    if not isinstance(log_entry, dict) or log_entry.get("tableId") != TABLE_IDS["Automation Log"]:
        raise ConfigError(
            f"GoL Base Automation Log table must be {TABLE_IDS['Automation Log']}."
        )
    if config.get("automationLogTableId") != TABLE_IDS["Automation Log"]:
        raise ConfigError(
            f"automationLogTableId must be {TABLE_IDS['Automation Log']} on GoL Base."
        )
    if config.get("automationInventoryTableId") != TABLE_IDS["Automation Inventory"]:
        raise ConfigError(
            "automationInventoryTableId must be "
            f"{TABLE_IDS['Automation Inventory']} on GoL Base."
        )
    if config.get("matchKeys") != gol_match_keys():
        raise ConfigError(
            "GoL Base matchKeys do not match the live Application and Applicant keys."
        )
    if config.get("fieldIds") != field_catalog():
        raise ConfigError("GoL Base fieldIds do not match the live field IDs.")


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("baseId") == RETIRED_ERP_BASE_ID:
        raise ConfigError(
            f"Configuration points at retired {RETIRED_ERP_BASE_NAME} "
            f"({RETIRED_ERP_BASE_ID}). Use {GOL_BASE_NAME} ({GOL_BASE_ID})."
        )
    for key, prefix in ID_PREFIXES.items():
        value = config.get(key)
        if not isinstance(value, str) or not value:
            raise ConfigError(f"Configuration is missing {key}.")
        if PLACEHOLDER.search(value):
            raise ConfigError(
                f"Configuration still holds the example placeholder for {key}. "
                "Replace it with the identifier from GoL Base."
            )
        if not value.startswith(prefix):
            raise ConfigError(f"Configuration value for {key} should start with {prefix!r}.")

    fields = config.get("fields")
    if not isinstance(fields, dict):
        raise ConfigError("Configuration is missing the fields map.")
    for key in REQUIRED_FIELD_KEYS:
        value = fields.get(key)
        if not isinstance(value, str) or not value:
            raise ConfigError(f"Configuration is missing the field id for fields.{key}.")
        if PLACEHOLDER.search(value):
            raise ConfigError(
                f"Configuration still holds the example placeholder for fields.{key}. "
                "Replace it with the field id from GoL Base."
            )
        if not value.startswith("fld"):
            raise ConfigError(f"Configuration value for fields.{key} should start with 'fld'.")

    organizations = config.get("organizations", {})
    if not isinstance(organizations, dict):
        raise ConfigError(
            "Configuration organizations must be a map of source name to Client Type."
        )

    tables = config.get("tables", {})
    if not isinstance(tables, dict):
        raise ConfigError("Configuration tables must be a map of table name to ids.")
    if "Case Task" in tables:
        raise ConfigError(
            "Configuration table 'Case Task' is the old GOL ERP name. "
            "GoL Base calls that table 'Assigned Tasks'."
        )
    for name, entry in tables.items():
        if not isinstance(entry, dict):
            raise ConfigError(f"Configuration table {name} must hold tableId and viewId.")
        for key, prefix in (("tableId", "tbl"), ("viewId", "viw")):
            value = entry.get(key)
            if not isinstance(value, str) or not value:
                raise ConfigError(f"Configuration table {name} is missing {key}.")
            if PLACEHOLDER.search(value):
                raise ConfigError(
                    f"Configuration still holds the example placeholder for table {name} {key}."
                )
            if not value.startswith(prefix):
                raise ConfigError(
                    f"Configuration table {name} {key} should start with {prefix!r}."
                )

    write_order = config.get("writeOrder")
    if config.get("baseId") == GOL_BASE_ID and write_order is None:
        raise ConfigError("GoL Base configuration is missing writeOrder.")
    if write_order is not None and list(write_order) != list(WRITE_ORDER):
        raise ConfigError(
            "writeOrder must be Application, Applicant, Historical, "
            "Team Assignment, Assigned Tasks."
        )
    if config.get("baseId") == GOL_BASE_ID:
        _validate_gol_destination(config)

    config.setdefault("automationName", "Applicant CSV to Airtable sync")
    config.setdefault("writerId", "applicant-csv-import")
    config.setdefault("organizations", {})
    config.setdefault("tables", {})
    return config

def table_link(config: dict[str, Any], table_name: str, record_id: str | None = None) -> str:
    """Build a table or direct record link from the configured ids."""
    try:
        entry = config["tables"][table_name]
    except KeyError as exc:
        raise ConfigError(f"No configured table named {table_name!r}.") from exc
    url = f"https://airtable.com/{config['baseId']}/{entry['tableId']}/{entry['viewId']}"
    return f"{url}/{record_id}" if record_id else url


def load_config(explicit: str | Path | None = None) -> dict[str, Any]:
    path = resolve_config_path(explicit)
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Configuration file is not valid JSON: {path}") from exc
    if not isinstance(config, dict):
        raise ConfigError(f"Configuration file must contain a JSON object: {path}")
    return validate_config(config)
