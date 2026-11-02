# Applicant CSV to Airtable sync

## Trigger

Use this when someone hands you an applicant or application CSV export and wants it applied to an Airtable base that already holds the same cases.

It runs only when you ask for it by name, and it has three modes. A vague request gets the read-only one.

| You say | Mode | What it does |
|---|---|---|
| "check this", "what would happen", or just the skill name | Audit | Reads code, config, and evidence. Writes nothing. |
| "preview", "dry run" | Preview | Compares your CSVs against live records and saves a local proposal. Writes nothing to Airtable. |
| "sync it", "apply this" | Apply | Writes the changes, logs the run, and produces client documents. |

It never opens the source system, never calls its API, and never goes looking for a CSV in a downloads folder. The files you attach or name are the only files it reads.

## Inputs

- Python 3.10 or later. No additional packages.
- One or more applicant CSV exports. [references/sample-applicant-export.csv](references/sample-applicant-export.csv) shows the header set and five fictional rows.
- A destination configuration: copy [references/config.example.json](references/config.example.json), fill in your own base, table, record, and field IDs, and keep it outside this repository.
- An Airtable personal access token with read and write access to that base, plus a CLI or MCP tool that can read and write records. The helpers read the token from `AIRTABLE_TOKEN` or an Airtable CLI profile at run time. No credential belongs in this package.
- Your own importer at `scripts/run_applicant_airtable_sync.py` in the project workspace. That part is project-specific and is **not** included here. This package ships the mode contract, the writer-check gate, the run log, the document contract, and the attachment verification around it.

## What happens

1. It asks for the CSVs and waits. Nothing else happens first.
2. It confirms what each file is and which organization it belongs to.
3. It previews. Proposed changes are reported as proposals, never as completed writes.
4. Before Apply, it checks whether anything else writes to the same tables. If another writer is active, or its state cannot be determined, Apply stops and says why. It will not disable a trigger or change a schedule to clear its own path.
5. It opens one Automation Log row with the outcome already set to `Failed`, so an interrupted run never looks successful.
6. It applies each source once, then reads the records back and compares again.
7. It writes the client documents, attaches them, and downloads each attachment to confirm the bytes match before claiming delivery.

## Outputs

Per run: one annotated diff CSV per source file, a client report, a field-level changes CSV, a review CSV, and a local sharing archive. See [examples](examples) for a fictional set of all five, plus [sample closing messages](examples/sample-run-output.md).

The originals are never modified. Each diff row gains the action taken, the result, the Airtable record ID, a direct record link, an issue link, a note, and a timestamp.

## Design decisions worth keeping

Most of the value here is in what the skill refuses to do:

- **A vague request gets the read-only mode.** "Take a look at this" is not authorization to write to a production base.
- **The log row starts at `Failed`.** A run that dies halfway leaves an accurate record instead of a hopeful one.
- **Writes completing and the run succeeding are separate claims.** 500 successful writes with 8 unresolved rows is a `Failed` run that did most of its job, and the closing message says both parts.
- **Organization is metadata, not a filter.** Rows from an organization you have not configured still sync; they just get no invented Client Type. Nothing is dropped for belonging to the wrong agency.
- **A missing staff match never blocks an applicant write,** but it does stop the run being marked `Succeeded`. The writes land; the report stays honest.
- **Identifier conflicts stay unresolved.** Two records that might be the same family are never merged on a name match. A renewal arriving with a new ID against an existing case is accepted only after readback proves a unique history event with the exact source date.
- **A blank identifier stays blank.** No value is invented to fill a required-looking column.
- **The action is judged separately from the result.** A row can be a confirmed `Updated` *and* need review. Collapsing those into "not changed" would hide a real write.
- **Calculated fields are labelled, not claimed.** A formula that recalculates after a write is recorded as `Observed`, not as something the sync did.
- **A matching filename is not delivery proof.** Every attachment is verified by name, byte size, and the SHA-256 of the downloaded file.
- **Applicant detail never reaches chat.** Names and row-level detail live in the client documents and the log row.

## Run it

Commands for all three modes are in [references/operations.md](references/operations.md). Set `APPLICANT_SYNC_CONFIG` once instead of passing `--config` every time:

```sh
export APPLICANT_SYNC_CONFIG=/path/outside/repository/applicant-sync-config.json

# Open the log row for this run.
python3 scripts/log_sync_run.py \
  --run-key applicant-sync-20260101T000000Z \
  --outcome Failed \
  --fields-written "No business records have been changed yet." \
  --notes "The sync is running. The final result is pending." \
  --reason "The sync has not finished." \
  --duration-ms 0

# Apply each CSV with your own importer, then close the same row with the
# terminal outcome and one --organization per source organization.

# Attach and verify the client documents.
python3 scripts/attach_log_documents.py \
  --run-key applicant-sync-20260101T000000Z \
  --docs-root <client-document-directory> \
  --documents <source-diff.csv> <client-report.md> <field-changes.csv> <review-items.csv>
```

Both helpers exit with code `2` and an explanation while any identifier is still an `XXXX` placeholder.

## Check the result

```sh
python3 -m unittest discover -s tests
```

The suite checks the mode contract, the writer-check gate, the attachment and reconciliation logic, the configuration validation, the example document formats, and that no real base ID, client name, credential, or personal file path is present in the package.

To also check for your own site-specific names before publishing a fork:

```sh
SKILL_DENYLIST='Your Agency,your-domain.org,A Person' python3 -m unittest discover -s tests
```

For a run itself: a trustworthy result names the mode, gives per-table counts, counts review items by kind, and links documents it has read back. Treat `Succeeded` with unresolved review items as a bug, not a rounding error.

## Limits

- Applicant and application exports only. Any other CSV type is refused rather than guessed at.
- Header sets vary between exports. Validation is against the required fields, not an exact column list.
- The importer itself is not included.
- The writer check reasons about the evidence available to it. It expires after 30 minutes, and the runner's own lock serializes only imports through that runner. It does not lock Airtable automations, other scripts, or external services.
- Attachments go through Airtable's direct upload path, capped at 5 MB per file.
- One base per configuration. Point it somewhere else and the run should refuse.
