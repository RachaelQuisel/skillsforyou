#!/usr/bin/env python3
"""backup.py — dump one Airtable base to a local directory. MVP.

See README.md for the full spec,
the backup behavior, and the list of things deliberately
out of MVP scope (restore, resume, sha256, S3 push).

Stdlib only. Python 3.10+.
"""

from __future__ import annotations

import argparse
import errno
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_ROOT = "https://api.airtable.com"
USER_AGENT = "airtable-backup-and-migrate/0.1.1-mvp"
RATE_LIMIT_SLEEP_S = 0.2  # ~5 req/sec/base, Airtable's documented cap
HTTP_TIMEOUT_S = 60
ATTACHMENT_TIMEOUT_S = 120
CHUNK_BYTES = 65_536

MIN_FREE_GB_DEFAULT = 5.0
ATTACHMENT_FLOOR_BYTES = 500 * 1024 * 1024  # 500 MB minimum headroom per attachment


class AirtableHTTPError(RuntimeError):
    """Raised on non-2xx from the Airtable API (after 429 retry)."""


class DiskFullAbort(RuntimeError):
    """Raised when free disk space drops below the safe floor."""


def read_pat(pat_path: Path) -> str:
    return pat_path.expanduser().read_text().strip()


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return slug[:40] or "base"


def free_bytes(path: Path) -> int:
    return shutil.disk_usage(path).free


def check_free_space(path: Path, need_bytes: int, context: str) -> None:
    """Abort with DiskFullAbort if free space would drop below `need_bytes`.

    `context` names what was about to be written, so the abort message
    tells the operator which file/table triggered it.
    """
    have = free_bytes(path)
    if have < need_bytes:
        raise DiskFullAbort(
            f"Free disk on {path}: {have / 1024 / 1024:.0f} MiB, need at least "
            f"{need_bytes / 1024 / 1024:.0f} MiB before writing {context}. "
            f"Aborting so the backup dir stays inspectable."
        )


def api_get(url: str, pat: str) -> dict:
    """GET a JSON endpoint. Retries once on 429. Rate-limits every call."""
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {pat}")
    req.add_header("User-Agent", USER_AGENT)
    try:
        try:
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = int(e.headers.get("Retry-After", "30"))
                print(f"  HTTP 429 rate limit; sleeping {retry_after}s and retrying", flush=True)
                time.sleep(retry_after)
                with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as resp:
                    return json.loads(resp.read())
            body = e.read().decode("utf-8", errors="replace")[:500]
            raise AirtableHTTPError(f"HTTP {e.code} on {url}: {body}") from e
    finally:
        time.sleep(RATE_LIMIT_SLEEP_S)


def resolve_base_name(pat: str, base_id: str) -> str:
    offset = None
    while True:
        url = f"{API_ROOT}/v0/meta/bases"
        if offset:
            url = f"{url}?offset={urllib.parse.quote(offset)}"
        data = api_get(url, pat)
        for b in data.get("bases", []):
            if b.get("id") == base_id:
                return b.get("name") or base_id
        offset = data.get("offset")
        if not offset:
            return base_id


def get_schema(pat: str, base_id: str) -> dict:
    return api_get(f"{API_ROOT}/v0/meta/bases/{base_id}/tables", pat)


def get_all_records(pat: str, base_id: str, table_id: str) -> list[dict]:
    """Page every record. returnFieldsByFieldId=true — always (best-practices §3)."""
    records: list[dict] = []
    offset: str | None = None
    while True:
        params = {"returnFieldsByFieldId": "true", "pageSize": "100"}
        if offset:
            params["offset"] = offset
        url = f"{API_ROOT}/v0/{base_id}/{table_id}?{urllib.parse.urlencode(params)}"
        data = api_get(url, pat)
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            return records


def safe_filename(name: str, fallback: str) -> str:
    if not name:
        return fallback
    cleaned = name.replace("/", "_").replace("\\", "_")
    if cleaned in (".", "..") or not cleaned.strip():
        return fallback
    return cleaned


def download_attachment(
    url: str, dest_path: Path, expected_size: int | None, backup_dir: Path
) -> int | None:
    """Stream bytes to disk. Free-space guarded. Returns bytes written, or None on HTTP error.

    Raises DiskFullAbort if the download would drive free space below the floor.
    Raises DiskFullAbort if a write hits ENOSPC mid-stream.
    """
    # Preflight: need max(500MB, expected_size * 2) — the *2 leaves room for the
    # records JSON write and any concurrent OS activity.
    need = max(ATTACHMENT_FLOOR_BYTES, (expected_size or 0) * 2)
    check_free_space(
        backup_dir,
        need,
        f"attachment {dest_path.relative_to(backup_dir)} "
        f"(size={expected_size or 'unknown'})",
    )

    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=ATTACHMENT_TIMEOUT_S) as resp:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            written = 0
            try:
                with open(dest_path, "wb") as f:
                    while True:
                        chunk = resp.read(CHUNK_BYTES)
                        if not chunk:
                            break
                        f.write(chunk)
                        written += len(chunk)
            except OSError as e:
                if e.errno == errno.ENOSPC:
                    raise DiskFullAbort(
                        f"Disk filled while streaming {dest_path.relative_to(backup_dir)} "
                        f"(wrote {written} bytes of expected {expected_size}). "
                        f"Partial file left on disk; safe to delete."
                    ) from e
                raise
            return written
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        print(f"    attachment download failed for {url[:80]}...: {e}", flush=True)
        return None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="backup.py",
        description="Back up one Airtable base (schema + records + attachments) to disk.",
    )
    p.add_argument("--base-id", required=True, help="Airtable base ID (appXXX...)")
    p.add_argument(
        "--pat-path",
        required=True,
        type=Path,
        help="File containing an Airtable PAT with data.records:read + schema.bases:read on the source base",
    )
    p.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        help="Parent directory. Backup lands at <out-dir>/<base-slug>-<UTC-timestamp>/",
    )
    p.add_argument(
        "--min-free-gb",
        type=float,
        default=MIN_FREE_GB_DEFAULT,
        help=f"Refuse to start if free disk on --out-dir is below this many GiB (default {MIN_FREE_GB_DEFAULT}).",
    )
    p.add_argument(
        "--skip-attachments",
        action="store_true",
        help="Back up schema + records only. Skip attachment file downloads. "
        "Attachment metadata (URL, filename, size) still preserved in records/*.json. "
        "Useful when disk is tight or you only need the schema+data.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    # Line-buffered stdout so tee / redirect show progress live, not after exit.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:
        pass  # Python < 3.7 wouldn't get us here anyway

    args = parse_args(argv)
    pat = read_pat(args.pat_path)
    base_id = args.base_id
    out_root = args.out_dir.expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    # Preflight disk check on the OUT-DIR partition (not always the same as ~).
    min_free_bytes = int(args.min_free_gb * 1024 * 1024 * 1024)
    have = free_bytes(out_root)
    print(
        f"Preflight: {have / 1024 / 1024 / 1024:.2f} GiB free on {out_root} "
        f"(minimum required: {args.min_free_gb:.2f} GiB)",
    )
    if have < min_free_bytes:
        print(
            f"REFUSED: free disk {have / 1024 / 1024 / 1024:.2f} GiB is below "
            f"--min-free-gb {args.min_free_gb:.2f}. Free space or lower the threshold. "
            f"If the base has few or small attachments, --skip-attachments can also fit.",
            file=sys.stderr,
        )
        return 2

    print(f"Fetching base name for {base_id} ...")
    base_name = resolve_base_name(pat, base_id)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    backup_dir = out_root / f"{slugify(base_name)}-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    (backup_dir / "records").mkdir(exist_ok=True)
    print(f"Backup directory: {backup_dir}")

    print("Fetching schema ...")
    schema = get_schema(pat, base_id)
    tables = schema.get("tables", [])
    schema_path = backup_dir / "schema.json"
    schema_body = json.dumps(
        {
            "base_id": base_id,
            "base_name_at_backup": base_name,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "tables": tables,
        },
        indent=2,
    )
    check_free_space(backup_dir, max(ATTACHMENT_FLOOR_BYTES, len(schema_body) * 2), "schema.json")
    schema_path.write_text(schema_body)
    print(f"Schema: {len(tables)} tables")

    total_records = 0
    total_attachments = 0
    total_attachment_bytes = 0
    warnings: list[str] = []
    per_table_counts: list[dict] = []
    aborted_reason: str | None = None

    try:
        for table in tables:
            tbl_id = table["id"]
            tbl_name = table.get("name", tbl_id)
            field_types = {f["id"]: f.get("type") for f in table.get("fields", [])}
            print(f"[{tbl_id}] {tbl_name}: fetching records ...")
            try:
                raw_records = get_all_records(pat, base_id, tbl_id)
            except AirtableHTTPError as e:
                msg = f"Table {tbl_id} ({tbl_name}) read failed: {e}"
                warnings.append(msg)
                print(f"  WARNING: {msg}")
                continue

            table_attachments = 0
            normalized: list[dict] = []
            for rec in raw_records:
                rec_id = rec["id"]
                cell_values = rec.get("fields", {})
                for fld_id, value in cell_values.items():
                    if field_types.get(fld_id) != "multipleAttachments":
                        continue
                    if not isinstance(value, list):
                        continue
                    for att_idx, att in enumerate(value):
                        if not isinstance(att, dict):
                            continue
                        url = att.get("url")
                        if not url:
                            continue
                        att_id = att.get("id", f"att{att_idx}")
                        if args.skip_attachments:
                            att["local_path"] = None
                            att["skipped_reason"] = "--skip-attachments"
                            continue
                        fname = safe_filename(att.get("filename", ""), att_id)
                        dest = backup_dir / "attachments" / tbl_id / rec_id / fname
                        if dest.exists():
                            dest = dest.with_name(f"{dest.stem}_{att_idx}{dest.suffix}")
                        written = download_attachment(
                            url, dest, att.get("size"), backup_dir
                        )
                        if written is None:
                            warnings.append(
                                f"Attachment download failed: {tbl_id}/{rec_id}/{att_id}"
                            )
                            att["local_path"] = None
                            att["download_error"] = True
                        else:
                            att["local_path"] = str(dest.relative_to(backup_dir))
                            att["local_bytes"] = written
                            table_attachments += 1
                            total_attachment_bytes += written
                            expected = att.get("size")
                            if expected and expected != written:
                                warnings.append(
                                    f"Attachment size mismatch: {tbl_id}/{rec_id}/{att_id} "
                                    f"expected={expected} got={written}"
                                )
                normalized.append(
                    {
                        "id": rec_id,
                        "createdTime": rec.get("createdTime"),
                        "cellValuesByFieldId": cell_values,
                    }
                )

            table_body = json.dumps(
                {
                    "table_id": tbl_id,
                    "table_name_at_backup": tbl_name,
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                    "record_count": len(normalized),
                    "records": normalized,
                },
                indent=2,
            )
            check_free_space(
                backup_dir,
                max(ATTACHMENT_FLOOR_BYTES, len(table_body) * 2),
                f"records/{tbl_id}.json",
            )
            try:
                (backup_dir / "records" / f"{tbl_id}.json").write_text(table_body)
            except OSError as e:
                if e.errno == errno.ENOSPC:
                    raise DiskFullAbort(
                        f"Disk filled while writing records/{tbl_id}.json"
                    ) from e
                raise

            per_table_counts.append(
                {
                    "table_id": tbl_id,
                    "table_name": tbl_name,
                    "records": len(normalized),
                    "attachments": table_attachments,
                }
            )
            total_records += len(normalized)
            total_attachments += table_attachments
            print(f"  {len(normalized)} records, {table_attachments} attachments")
    except DiskFullAbort as e:
        aborted_reason = str(e)
        print(f"ABORTED: {aborted_reason}", file=sys.stderr)

    # Always try to write MANIFEST so the operator has a record of what landed.
    manifest = {
        "format_version": "1",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "base_id": base_id,
        "base_name_at_backup": base_name,
        "backup_tool_version": "0.1.1-mvp",
        "aborted": aborted_reason is not None,
        "aborted_reason": aborted_reason,
        "counts": {
            "tables_in_schema": len(tables),
            "tables_processed": len(per_table_counts),
            "records_total": total_records,
            "attachments_total": total_attachments,
            "attachment_bytes_total": total_attachment_bytes,
        },
        "per_table": per_table_counts,
        "warnings": warnings,
    }
    manifest_body = json.dumps(manifest, indent=2)
    try:
        (backup_dir / "MANIFEST.json").write_text(manifest_body)
    except OSError as e:
        # If we can't even write the manifest, print it to stderr so the
        # operator has SOME record of what state we got to.
        print(f"MANIFEST write failed ({e}); printing to stderr:", file=sys.stderr)
        print(manifest_body, file=sys.stderr)

    if aborted_reason:
        print(
            f"BACKUP ABORTED (partial): base={base_id} tables_processed="
            f"{len(per_table_counts)}/{len(tables)} records={total_records} "
            f"attachments={total_attachments} bytes={total_attachment_bytes} "
            f"dir={backup_dir}",
            file=sys.stderr,
        )
        print("The partial dir is intact for inspection. Delete when done.", file=sys.stderr)
        return 3
    ok_line = (
        f"BACKUP OK: base={base_id} tables={len(tables)} "
        f"records={total_records} attachments={total_attachments} "
        f"bytes={total_attachment_bytes} dir={backup_dir}"
    )
    if warnings:
        print(f"BACKUP COMPLETED WITH {len(warnings)} WARNING(S):")
        for w in warnings:
            print(f"  - {w}")
        print(ok_line)
        return 1
    print(ok_line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
