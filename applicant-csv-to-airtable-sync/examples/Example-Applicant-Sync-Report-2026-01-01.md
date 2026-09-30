# Example Agency applicant update report: January 1, 2026

Every organization, person, identifier, link, and date in this document is invented. The counts come from one real run, kept so the arithmetic in the example is consistent. Nothing here identifies a real applicant, worker, or agency.

## Results

Two source files were applied. The sync created 245 records and updated 267 existing records. Records created during this run are not counted again as updates.

| Change | Records |
| --- | --- |
| Created | 245 |
| Existing records updated | 267 |

The sync log outcome is **Failed**. The writes above completed normally. The outcome stays Failed because ten source rows still need review, listed below. A Failed outcome here means "not finished", not "nothing worked".

Sync log: `https://airtable.com/appExample01/tblLog01/viwLog01/recLogExample`

## Source results

| Source file | Rows | Finished | Needs follow-up | Needs review |
| --- | --- | --- | --- | --- |
| Example-Applications-Diff-2026-01-01.csv | 222 | 219 | 3 | 0 |
| Example-Renewals-Diff-2026-01-01.csv | 662 | 657 | 4 | 1 |

Source actions are counted separately from results, because one source row can change several tables.

| Source file | No change | Created | Updated | Not changed |
| --- | --- | --- | --- | --- |
| Example-Applications-Diff-2026-01-01.csv | 192 | 16 | 14 | 0 |
| Example-Renewals-Diff-2026-01-01.csv | 466 | 17 | 178 | 1 |

## Items to review

Ten source rows need a decision. Nothing was merged, overwritten, or guessed. The full list with links is in `Example-Review-Items-2026-01-01.csv`.

| Issue type in the CSV | What it means | Rows |
| --- | --- | --- |
| `stable-field-conflict` | Two different application IDs claim the same case. | 3 |
| `ambiguous-linked-applicant-identity` | Two Applicant records could be the same person. | 1 |
| `unmatched-linked-applicant-identity` | No linked Applicant name matches the source exactly, and the source carries no stable person ID. | 1 |
| `linked-applicant-person-id-conflict` | The name matches exactly, but the Applicant already holds a different person ID. | 1 |
| `unmatched-staff` | A worker named in the source is not in Staff. | 4 |

Next steps:

- For each ID conflict, confirm which application ID belongs to the case. The existing value was kept until you decide.
- For the person matches, confirm the correct Applicant. Nothing on those records was changed, and no duplicate was created to work around the mismatch.
- For the person-ID conflict, confirm which stable ID belongs to the applicant. A matching name was not treated as permission to overwrite an identifier.
- For each unmatched worker, add or confirm the person in Staff. The application writes completed without the assignment link.

A missing worker never blocks an application write. It does keep the run from being marked Succeeded. A person map can supply stable person IDs by application and household role; it never authorizes a guessed name alias.

## Renewal records

The base keeps one case per RFA. When a renewal arrives with a new application ID, the original case ID is kept and the renewal is recorded as a separate history event.

72 renewal application IDs were confirmed this way. Each has one unique Historical Status Change event with the exact source date, linked to the uniquely matched RFA case. The verified event link is in the renewals diff CSV on each affected row.

Renewal IDs without that evidence were not accepted. They appear in the review CSV instead.

## Tables changed

| Table | Table ID | Created | Existing updated | Records with changes observed |
| --- | --- | --- | --- | --- |
| Application | `tblApp01` | 33 | 175 | 212 |
| Applicant | `tblApl01` | 50 | 62 | 183 |
| Historical | `tblHis01` | 124 | 0 | 188 |
| Team Assignment | `tblTeam01` | 38 | 0 | 65 |
| Case Task | `tblTask01` | 0 | 30 | 182 |
| Automation Log | `tblLog01` | 0 | 0 | 1 |

"Records with changes observed" is higher than created plus updated in some tables. Two reasons: calculated fields recalculate on their own, and the before and after snapshots are separate reads, so other activity in the base can land between them. Only confirmed writes are attributed to this sync.

The Automation Log row is this run's own log entry. It is not a business record.

## Fields changed

4,884 field-level changes were recorded. Before and after values for every one are in `Example-Field-Changes-2026-01-01.csv`. A representative 13 rows are included in that example file.

| Table | Field | Field ID | Type |
| --- | --- | --- | --- |
| Application | Binti Application ID | `fldAppBid` | Single line text |
| Application | Status | `fldAppSts` | Single select |
| Application | Client Type | `fldAppCli` | Single select |
| Application | Renewal Due Date | `fldAppRdd` | Date |
| Application | Days In Status | `fldAppDis` | Formula |
| Applicant | Email | `fldAplEml` | Email |
| Historical | Status Change Date | `fldHisDte` | Date |
| Team Assignment | Staff Member | `fldTeaStf` | Linked record |
| Case Task | Due Date | `fldTskDue` | Date |

### Field type guide

- **Single line text** holds one line of plain text. Identifiers live here.
- **Single select** allows one value from a fixed list. A value that is not already on the list has to be added to the field before it can be saved.
- **Date** holds a calendar date.
- **Email** holds one address and is validated by Airtable.
- **Linked record** points at a record in another table. It stores the link, not a copy of the name.
- **Formula** is calculated by Airtable from other fields. The sync never writes one. A formula field can change on its own after a write, which is why it is labeled Observed rather than Updated in the detailed CSV.

## Files to use

- `Example-Applicant-Sync-Report-2026-01-01.md` — this report.
- `Example-Applications-Diff-2026-01-01.csv` — the first source file, with the outcome for each row.
- `Example-Renewals-Diff-2026-01-01.csv` — the second source file, with the outcome for each row and the verified renewal event links.
- `Example-Field-Changes-2026-01-01.csv` — every field that changed, with before and after values.
- `Example-Review-Items-2026-01-01.csv` — the eight rows that need a decision, with direct links.

The original source files were not modified.

## Run reference

- Base ID: `appExample01`
- Run key: `applicant-sync-20260101T000000Z`
- Preservation check: the original source files were compared against their saved copies after the run and were unchanged.
- Verification limits: snapshots before and after the run are separate reads, so activity by other people or automations can appear in the observed counts. Created and updated counts come from write receipts and are attributed to this sync only.
