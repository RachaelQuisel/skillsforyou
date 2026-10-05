# Targets and data rules

## Configure the destination

The live destination is GoL Base, `appcxLcvRF7dWQOHH`. The retired GOL ERP base is `appp6pbBbaxuOLu2v`. A live schema read shows that ID is GOL ERP, not GoL Base. Application's `GOL ERP Base RecID` (`fldtVbqKPooJGhu5A`) was the migration upsert key. This sync does not match on it.

Copy [config.example.json](config.example.json) to a path outside this repository, fill the remaining view IDs and Automation Log field IDs, and point the helpers at it with `--config <path>` or `APPLICANT_SYNC_CONFIG=<path>`. Both helpers exit with code `2` while any value still holds an `XXXX` placeholder. The example already names GoL Base and the live table IDs. View IDs were not in the schema read used for this retarget, so they stay placeholders until filled from the live base. A config that uses the retired base ID, or a table named `Case Task`, is rejected.

| Setting | Value |
|---|---|
| Project | The current project workspace. |
| Base | GoL Base `appcxLcvRF7dWQOHH`. |
| Automation Inventory | `automationInventoryTableId` (`tblIrEObjqmmqzAHb`), record `automationInventoryRecordId`. |
| Automation Log | `automationLogTableId` (`tblprCx6rMOrVNhrf`). |
| Runner | `<project-workspace>/scripts/run_applicant_airtable_sync.py`. |
| Private run root | `<project-workspace>/.runtime/applicant-csv-to-airtable-sync/<run-key>`. |
| Client document root | `<project-workspace>/docs/applicant-csv-to-airtable-sync/<run-key>`. |
| Log helper | `scripts/log_sync_run.py` in this skill. |
| Attachment helper | `scripts/attach_log_documents.py` in this skill. |

The runner is project-specific and is not part of this skill package. This package does not include `scripts/run_applicant_airtable_sync.py`. Supply your own importer with the same flags.

A run uses the GoL Base ID in the configuration. Refresh table and field definitions before Apply. Use field IDs for writes and live names for reports. A renamed field keeps its ID; a name lookup fails as though it were a permission problem.

Configure one entry per table you want linked, in the configuration's `tables` block. Build a table link as `https://airtable.com/<base-id>/<table-id>/<view-id>`. Append `/<record-id>` for a direct record link. Linked-record fields store record IDs, not display names.

## Match keys

Reads set `returnFieldsByFieldId` to true. `filterByFormula` uses `{fieldId}` and `fieldsToMergeOn` uses field IDs. A label is the current name only. Strip a leading U+FEFF from each Binti header, then map:

| CSV header, kept as Binti writes it | Table | Label | Field ID | API use |
|---|---|---|---|---|
| `Binti application id` | Application `tblle86w7gTHmBsDS` | Binti ID | `fldsxEB5mSLl3MBK6` | Upsert key, looked up on its own |
| `Rfa id` | Application | RFA ID | `fldR9l7Jjm6Gr9yJV` | Upsert key, looked up on its own |
| `Status` | Application | Case Status | `fld3HrhY9xh9EWTso` | Write |
|  | Application | Applicants | `fldITF9OcRYSU952a` | Link, record IDs |
|  | Application | Assignment | `fldw87HpCuFHjUdiQ` | Link, record IDs |
|  | Application | Events | `fldTn1SLNUBnELbUT` | Link to Historical, record IDs |
|  | Application | Case Task | `fldFxMTIjCttt2vC9` | Link to Assigned Tasks, record IDs |
|  | Application | GOL ERP Base RecID | `fldtVbqKPooJGhu5A` | Not an upsert key and not written |
| Person ID, when supplied | Applicant `tblZsYxi9G7MVI7p5` | Binti Person ID | `flddz0UmEcHGNreOF` | Upsert key |
|  | Applicant | RFA ID (from Applications) | `fldnNRWueleJKZWtV` | Lookup. Not an upsert key |
|  | Historical `tbl3VYr0NXusmTu7X` | Application | `fldrhq6h7Y5kUjRBe` | Link, record IDs |

Airtable ANDs every ID in one `fieldsToMergeOn` list, so each lookup is its own formula and a write merges on the one field ID that matched. A blank `Rfa id` stays out of both. GoL Base has neither `Binti application id` nor `Rfa id`. Those were GOL ERP field names, and one copy of `Binti application id` began with U+FEFF.

Upsert Applicant on `flddz0UmEcHGNreOF` only when a person ID is supplied. The sample export has no person-id column. `Applicant external identifier` and `Co-applicant external identifier` are not that key. Never match a person by phone or email.

Write in this order: Application, Applicant, Historical (`tbl3VYr0NXusmTu7X`), Team Assignment (`tblmNxsRPLxsxSNbr`), Assigned Tasks (`tblVB0TYikSrpf2tg`). Assigned Tasks is the table this skill used to call Case Task. Staff is `tbltuqSEdJuKk6763`.

Fields this skill still needs, and whose IDs were not in the schema summary, are `UNRESOLVED_FIELDS` in `scripts/sync_config.py`. No ID was invented for them. They include Client Type, Staff Member, Historical Date, Historical Type, the Assigned Tasks Application link, Applicant Name, Staff Name, and the Automation Log fields. View IDs and the Automation Inventory record ID are also still unknown.

A blank source cell does not authorize erasing an Airtable value.

## Source ownership

- Require `Binti application id`, `Rfa id`, `Applicant name`, `CBOs`, `Status`, and `Application started as` headers. These are the column names the source system writes, so they are matched literally after stripping a leading BOM. Validate the current runner's remaining required headers.
- Header sets vary between exports. One export names a column `Days since child placed` where another names it `Days from child placed to application approved`. Validate against the required fields, not an exact column list.
- Preserve every `CBOs` organization. Map each organization named in the configuration's `organizations` block to its Client Type. Do not invent a Client Type for another organization.
- Apply nonblank mapped source values with `--source-wins`. Protect stable identifiers and Airtable-only operational fields. A blank source cell does not authorize erasing an Airtable value.
- Update Application and Applicant using the match keys above. Include valid Historical, Team Assignment, and Assigned Tasks changes. Do not extend the mapping during an import.

See [sample-applicant-export.csv](sample-applicant-export.csv) for the full header set and five fictional rows covering a blank RFA, a renewal reusing an existing RFA, an unknown worker, an unconfigured organization, and an ICWA row.

## Identity and staff

- Prefer unique stable source identifiers. Upsert Application on `Binti ID` and `RFA ID`. Use the existing RFA case only when the match is unique. Never replace a disputed stable identifier.
- Match full normalized names exactly when the current code permits name evidence. Do not infer aliases, use surname tokens, accept spelling similarity, or fall back to an unrelated contact. A reviewed application-and-role mapping may provide a `Binti Person ID`. It does not create a name alias. Never match an Applicant by phone or email.
- Preserve ambiguous Applicant links and values. Report the candidate records and related Application. Do not merge, guess, or create a duplicate to avoid review.
- A unique source `Binti application id` is sufficient when the source `Rfa id` is blank. Leave `RFA ID` blank.
- Keep one case per RFA. Account for a different renewal application ID only after readback confirms its unique Historical Status Change event, exact source date, and link to the unique RFA case. Otherwise, leave the identifier difference unresolved.
- Link Staff only after a unique verified match. A missing Staff match does not block other valid writes. It still prevents a Succeeded outcome. Do not create Staff or default an unknown role to a guessed one. Leave an unverified role blank.

## Evidence

Keep snapshots, raw verification, mutation receipts, writer checks, and recovery archives private. Store no credentials in the skill. The attachment helper reads a token from `AIRTABLE_TOKEN` or an Airtable CLI profile at run time. Keep personal values out of diagnostic output and aggregate Automation Log notes. Use [client-documents.md](client-documents.md) for the detailed records needed by the client.
