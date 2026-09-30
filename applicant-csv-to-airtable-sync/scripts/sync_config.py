#!/usr/bin/env python3
"""Load the Airtable destination configuration for the applicant CSV sync.

No base, table, record, or field identifier is hardcoded in this skill. Copy
``references/config.example.json``, fill in the identifiers for your own base,
and point the scripts at it with ``--config`` or the ``APPLICANT_SYNC_CONFIG``
environment variable.
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


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    for key, prefix in ID_PREFIXES.items():
        value = config.get(key)
        if not isinstance(value, str) or not value:
            raise ConfigError(f"Configuration is missing {key}.")
        if PLACEHOLDER.search(value):
            raise ConfigError(
                f"Configuration still holds the example placeholder for {key}. "
                "Replace it with the identifier from your own base."
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
                "Replace it with the field id from your own base."
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
