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

# Application.GOL ERP Base RecID was the migration upsert key. It is not a CSV key.
MIGRATION_RECID_FIELD = "GOL ERP Base RecID"
MIGRATION_RECID_FIELD_ID = "fldtVbqKPooJGhu5A"

PERSON_ID_WHEN = (
    "Only when the CSV or the reviewed person map supplies a person ID. "
    "Do not use Applicant external identifier, phone, or email."
)
PERSON_ID_HEADERS = frozenset({"binti person id", "person id"})

DOCUMENTED_AIRTABLE_IDS = frozenset(
    {
        GOL_BASE_ID,
        RETIRED_ERP_BASE_ID,
        *TABLE_IDS.values(),
        "fldsxEB5mSLl3MBK6",
        "fldR9l7Jjm6Gr9yJV",
        "flddz0UmEcHGNreOF",
        MIGRATION_RECID_FIELD_ID,
    }
)


def gol_match_keys() -> dict[str, list[dict[str, str]]]:
    """Airtable fields this sync upserts on. CSV headers stay as Binti writes them."""
    return {
        "Application": [
            {
                "csvHeader": "Binti application id",
                "field": "Binti ID",
                "fieldId": "fldsxEB5mSLl3MBK6",
            },
            {
                "csvHeader": "Rfa id",
                "field": "RFA ID",
                "fieldId": "fldR9l7Jjm6Gr9yJV",
            },
        ],
        "Applicant": [
            {
                "field": "Binti Person ID",
                "fieldId": "flddz0UmEcHGNreOF",
                "when": PERSON_ID_WHEN,
            },
        ],
    }


def normalize_csv_header(header: str) -> str:
    """Drop a leading BOM. GOL ERP stored one copy of the application id with U+FEFF."""
    return header.lstrip("\ufeff").strip()


def application_field_for_csv_header(header: str) -> str | None:
    """Map a Binti CSV header to the GoL Base Application field it writes."""
    cleaned = normalize_csv_header(header)
    for item in gol_match_keys()["Application"]:
        if cleaned == item["csvHeader"]:
            return item["field"]
    return None


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
