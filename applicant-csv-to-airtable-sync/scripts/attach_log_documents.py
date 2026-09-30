#!/usr/bin/env python3
"""Attach the client documents to one exact Airtable Automation Log row.

A matching filename is not delivery proof. Every document is verified by
filename, byte size, and the SHA-256 digest of the downloaded attachment.

Destination identifiers come from the configuration file described in
``references/config.md``. Nothing about a specific base is hardcoded here.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sync_config import ConfigError, load_config  # noqa: E402


DEFAULT_DOCS_ROOT = Path.cwd() / "docs"
MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024
PRIVATE_FILENAME_MARKERS = (
    ".private.",
    "record-manifest",
    "identifier-conflicts",
    "mutation-receipt",
    "person-map",
    "downstream-before",
    "downstream-after",
    "direct-records",
    "evidence-summary",
)


def validate_document_paths(paths: Iterable[Path], docs_root: Path) -> list[Path]:
    root = docs_root.expanduser().resolve()
    validated: list[Path] = []
    for path in paths:
        resolved = path.expanduser().resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Document is outside the client-safe docs root: {resolved}") from exc
        if not resolved.is_file():
            raise ValueError(f"Document does not exist: {resolved}")
        lowered_name = resolved.name.lower()
        if any(marker in lowered_name for marker in PRIVATE_FILENAME_MARKERS):
            raise ValueError(f"Refusing to attach a private artifact: {resolved.name}")
        if resolved.stat().st_size > MAX_ATTACHMENT_BYTES:
            raise ValueError(f"Document exceeds Airtable's 5 MB direct-upload limit: {resolved.name}")
        validated.append(resolved)
    if not validated:
        raise ValueError("At least one client-safe document is required")
    if len({path.name for path in validated}) != len(validated):
        raise ValueError("Document filenames must be unique within one run")
    return validated


def resolve_log_record(
    payload: dict[str, Any],
    run_key: str,
    run_key_field_id: str,
    attachment_field_id: str,
) -> tuple[str, set[str]]:
    matches = [
        record
        for record in payload.get("records", [])
        if record.get("cellValuesByFieldId", {}).get(run_key_field_id) == run_key
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one Automation Log record for the stable run key; found {len(matches)}"
        )
    record = matches[0]
    attachments = record.get("cellValuesByFieldId", {}).get(attachment_field_id) or []
    filenames = {
        attachment["filename"]
        for attachment in attachments
        if isinstance(attachment, dict) and attachment.get("filename")
    }
    return str(record["id"]), filenames


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read(MAX_ATTACHMENT_BYTES + 1)


def exact_attachment(
    attachments: Iterable[dict[str, Any]],
    document: Path,
    downloader: Callable[[str], bytes] = download_bytes,
) -> dict[str, Any] | None:
    expected_size = document.stat().st_size
    expected_digest = file_sha256(document)
    for item in attachments:
        if (
            item.get("filename") != document.name
            or not item.get("id")
            or not item.get("url")
            or int(item.get("size", -1)) != expected_size
        ):
            continue
        content = downloader(str(item["url"]))
        if len(content) > MAX_ATTACHMENT_BYTES:
            raise RuntimeError("Airtable attachment exceeds the direct-upload limit")
        if len(content) == expected_size and hashlib.sha256(content).hexdigest() == expected_digest:
            return item
    return None


def run_airtable_cli(arguments: list[str], profile: str | None = None) -> dict[str, Any]:
    command = ["airtable-mcp", *arguments, "-q"]
    if profile:
        command.extend(["--profile", profile])
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def fetch_log_records(
    run_key: str,
    base_id: str,
    table_id: str,
    run_key_field_id: str,
    attachment_field_id: str,
    profile: str | None,
) -> dict[str, Any]:
    filters = {
        "operator": "and",
        "operands": [{"operator": "=", "operands": [run_key_field_id, run_key]}],
    }
    return run_airtable_cli(
        [
            "list-records-for-table",
            "--baseId",
            base_id,
            "--tableId",
            table_id,
            "--filters",
            json.dumps(filters, separators=(",", ":")),
            "--fieldIds",
            json.dumps([run_key_field_id, attachment_field_id]),
            "--pageSize",
            "3",
        ],
        profile,
    )


def load_airtable_token(profile: str | None = None) -> str:
    environment_token = os.environ.get("AIRTABLE_TOKEN")
    if environment_token:
        return environment_token
    config_path = Path.home() / ".airtable" / "cli.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    profile_name = profile or config.get("defaultProfile") or "default"
    try:
        return str(config["profiles"][profile_name]["token"])
    except KeyError as exc:
        raise RuntimeError(f"Airtable CLI profile is missing a token: {profile_name}") from exc


def upload_document(
    path: Path,
    token: str,
    base_id: str,
    record_id: str,
    attachment_field_id: str,
) -> None:
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    payload = {
        "contentType": content_type,
        "file": base64.b64encode(path.read_bytes()).decode("ascii"),
        "filename": path.name,
    }
    url = (
        f"https://content.airtable.com/v0/{base_id}/{record_id}/"
        f"{attachment_field_id}/uploadAttachment"
    )
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status < 200 or response.status >= 300:
                raise RuntimeError(f"Airtable attachment upload returned HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Airtable attachment upload failed with HTTP {exc.code}: {body}") from exc


def attach_documents(
    run_key: str,
    documents: list[Path],
    base_id: str,
    table_id: str,
    run_key_field_id: str,
    attachment_field_id: str,
    profile: str | None,
    uploader: Callable[[Path, str, str, str, str], None] = upload_document,
    downloader: Callable[[str], bytes] = download_bytes,
) -> dict[str, Any]:
    def fetch() -> tuple[str, list[dict[str, Any]]]:
        payload = fetch_log_records(
            run_key, base_id, table_id, run_key_field_id, attachment_field_id, profile,
        )
        record_id, _ = resolve_log_record(payload, run_key, run_key_field_id, attachment_field_id)
        record = next(record for record in payload["records"] if record["id"] == record_id)
        return record_id, record.get("cellValuesByFieldId", {}).get(attachment_field_id) or []

    record_id, before = fetch()
    pending = [path for path in documents if exact_attachment(before, path, downloader) is None]
    token = load_airtable_token(profile) if pending else ""
    for document in pending:
        uploader(document, token, base_id, record_id, attachment_field_id)

    final_record_id, attachments = fetch()
    if final_record_id != record_id:
        raise RuntimeError("The run key resolved to a different Automation Log record")
    selected_ids: list[dict[str, str]] = []
    for document in documents:
        match = exact_attachment(attachments, document, downloader)
        if match is None:
            raise RuntimeError(f"Airtable attachment contents could not be verified: {document.name}")
        selected_ids.append({"id": str(match["id"])})
    removed = len(attachments) - len(selected_ids)
    if removed:
        run_airtable_cli(
            [
                "update-records-for-table", "--baseId", base_id, "--tableId", table_id,
                "--records", json.dumps([
                    {"id": record_id, "fields": {attachment_field_id: selected_ids}}
                ], separators=(",", ":")),
                "--fieldIds", json.dumps([attachment_field_id]),
            ], profile,
        )
    verified_record_id, verified = fetch()
    if verified_record_id != record_id or len(verified) != len(documents):
        raise RuntimeError("Airtable attachment reconciliation did not produce the exact document set")
    if {item.get("filename") for item in verified} != {path.name for path in documents}:
        raise RuntimeError("Airtable attachment reconciliation did not produce the exact document set")
    for document in documents:
        if exact_attachment(verified, document, downloader) is None:
            raise RuntimeError(f"Airtable final attachment contents could not be verified: {document.name}")
    return {
        "requested": len(documents), "uploaded": len(pending),
        "alreadyAttached": len(documents) - len(pending), "verified": len(documents),
        "removed": removed,
        "sha256": {path.name: file_sha256(path) for path in documents},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to the destination configuration JSON.")
    parser.add_argument("--run-key", required=True)
    parser.add_argument("--documents", nargs="+", type=Path, required=True)
    parser.add_argument("--docs-root", type=Path, default=DEFAULT_DOCS_ROOT)
    parser.add_argument("--profile")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    documents = validate_document_paths(args.documents, args.docs_root)
    result = attach_documents(
        args.run_key,
        documents,
        config["baseId"],
        config["automationLogTableId"],
        config["fields"]["runKey"],
        config["fields"]["clientDocuments"],
        args.profile,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
