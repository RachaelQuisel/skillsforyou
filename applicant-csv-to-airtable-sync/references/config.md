# Targets and data rules

## Configure the destination

No base, table, record, or field identifier is hardcoded in this skill. Copy [config.example.json](config.example.json) to a path outside this repository, fill in the identifiers from your own base, and point the helpers at it with `--config <path>` or `APPLICANT_SYNC_CONFIG=<path>`. Both helpers exit with code `2` while any value still holds an `XXXX` placeholder.

| Setting | Value |
|---|---|
| Project | The current project workspace. |
| Base | `baseId` in the configuration. |
| Automation Inventory | `automationInventoryTableId`, record `automationInventoryRecordId`. |
| Automation Log | `automationLogTableId`. |
| Runner | `<project-workspace>/scripts/run_applicant_airtable_sync.py`. |
| Private run root | `<project-workspace>/.runtime/applicant-csv-to-airtable-sync/<run-key>`. |
| Client document root | `<project-workspace>/docs/applicant-csv-to-airtable-sync/<run-key>`. |
| Log helper | `scripts/log_sync_run.py` in this skill. |
| Attachment helper | `scripts/attach_log_documents.py` in this skill. |

The runner is project-specific and is not part of this skill package. Supply your own importer with the same flags.

Reject any other base. Refresh table and field definitions before Apply. Use field IDs for writes and live names for reports. A renamed field keeps its ID; a name lookup fails as though it were a permission problem.

Configure one entry per table you want linked, in the configuration's `tables` block. Build a table link as `https://airtable.com/<base-id>/<table-id>/<view-id>`. Append `/<record-id>` for a direct record link.

## Source ownership

- Require `Binti application id`, `Rfa id`, `Applicant name`, `CBOs`, `Status`, and `Application started as` headers. These are the column names the source system writes, so they are matched literally. Validate the current runner's remaining required headers.
- Header sets vary between exports. One export names a column `Days since child placed` where another names it `Days from child placed to application approved`. Validate against the required fields, not an exact column list.
- Preserve every `CBOs` organization. Map each organization named in the configuration's `organizations` block to its Client Type. Do not invent a Client Type for another organization.
- Apply nonblank mapped source values with `--source-wins`. Protect stable identifiers and Airtable-only operational fields. A blank source cell does not authorize erasing an Airtable value.
- Update both Application and Applicant as supported by the current mapping. Include valid Historical, Team Assignment, and Case Task changes. Do not extend the mapping during an import.

See [sample-applicant-export.csv](sample-applicant-export.csv) for the full header set and five fictional rows covering a blank RFA, a renewal reusing an existing RFA, an unknown worker, an unconfigured organization, and an ICWA row.

## Identity and staff

- Prefer unique stable source identifiers. Use the existing RFA case only when the match is unique. Never replace a disputed stable identifier.
- Match full normalized names exactly when the current code permits name evidence. Do not infer aliases, use surname tokens, accept spelling similarity, or fall back to an unrelated contact. A reviewed application-and-role mapping may provide a stable Person ID. It does not create a name alias.
- Preserve ambiguous Applicant links and values. Report the candidate records and related Application. Do not merge, guess, or create a duplicate to avoid review.
- A unique source application ID is sufficient when the source RFA is blank. Leave the RFA blank.
- Keep one case per RFA. Account for a different renewal application ID only after readback confirms its unique Historical Status Change event, exact source date, and link to the unique RFA case. Otherwise, leave the identifier difference unresolved.
- Link Staff only after a unique verified match. A missing Staff match does not block other valid writes. It still prevents a Succeeded outcome. Do not create Staff or default an unknown role to a guessed one. Leave an unverified role blank.

## Evidence

Keep snapshots, raw verification, mutation receipts, writer checks, and recovery archives private. Store no credentials in the skill. The attachment helper reads a token from `AIRTABLE_TOKEN` or an Airtable CLI profile at run time. Keep personal values out of diagnostic output and aggregate Automation Log notes. Use [client-documents.md](client-documents.md) for the detailed records needed by the client.
