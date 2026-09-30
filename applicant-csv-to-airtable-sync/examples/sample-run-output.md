# Sample closing messages

The closing message is the part the user actually reads. These three examples show the shape. Every name, path, and organization is invented; the counts come from one real run so the arithmetic is consistent.

## A run with review items

```text
Finished. Mode: Apply.

Records written:
- Application: 33 created, 175 updated
- Applicant: 50 created, 62 updated
- Historical: 124 created
- Team Assignment: 38 created
- Case Task: 30 updated
Totals: 245 created, 267 existing records updated.

Source rows:
- Example-Applications-Diff: 222 rows — 219 finished, 3 need follow-up
- Example-Renewals-Diff: 662 rows — 657 finished, 4 need follow-up, 1 needs review

Ten rows need a decision: 3 application-ID conflicts, 1 ambiguous Applicant
match, 1 linked applicant with no exact name match, 1 conflicting person ID,
4 workers not found in Staff. Nothing was merged or overwritten.

The writes above are complete. The log stays Failed until those ten are
resolved.

Client documents (attached to the log and verified by content):
- Report: <client-docs>/Example-Applicant-Sync-Report-2026-01-01.md
- Applications diff: <client-docs>/Example-Applications-Diff-2026-01-01.csv
- Renewals diff: <client-docs>/Example-Renewals-Diff-2026-01-01.csv
- Field changes: <client-docs>/Example-Field-Changes-2026-01-01.csv
- Review items: <client-docs>/Example-Review-Items-2026-01-01.csv
- Sharing archive: <client-docs>/Example-Client-Documents-2026-01-01.zip

Changed tables: Application, Applicant, Historical, Team Assignment,
Case Task, and Automation Log.
```

Five rules are doing work in that message:

- **Counts are per table, not just a total.** "245 created" does not tell anyone which table grew, or whether the growth was applications or history rows.
- **Source-row results are reported separately from record counts.** One source row can touch five tables, so 884 source rows and 512 record changes are both true and neither is a restatement of the other.
- **Review items are counted by kind.** ID conflicts, unresolved person matches, conflicting person IDs, and missing workers are four different problems with four different fixes. "Ten need review" hides that.
- **"Writes complete" and "run succeeded" are kept apart.** The message says both things in the same breath, because a Failed log with 512 successful writes is the normal, honest outcome when something still needs a human.
- **The mode is stated.** A Preview and an Apply produce similar-looking numbers. Only one of them changed anything, so the message says which it was.
- **Documents are named as verified.** The helper checks filename, byte size, and the SHA-256 of the downloaded attachment. A matching filename alone is not delivery proof.

## A clean run

```text
Finished. Mode: Apply.

Records written:
- Application: 12 created, 40 updated
- Applicant: 9 created, 11 updated
Totals: 21 created, 51 existing records updated.

Source rows: Example-Applications-Diff: 260 rows — 260 finished.

No rows need review. The log is marked Succeeded.

Client documents (attached to the log and verified by content):
- Report: <client-docs>/Example-Applicant-Sync-Report-2026-01-01.md
- Applications diff: <client-docs>/Example-Applications-Diff-2026-01-01.csv
- Field changes: <client-docs>/Example-Field-Changes-2026-01-01.csv
- Review items: <client-docs>/Example-Review-Items-2026-01-01.csv (header only)

Changed tables: Application, Applicant, and Automation Log.
```

The review CSV is still produced with only its header row. A missing file is ambiguous; an empty one is not.

## A preview

```text
Finished. Mode: Preview. Nothing was written to Airtable.

Proposed changes:
- Application: 33 to create, 175 to update
- Applicant: 50 to create, 62 to update

Proposed source rows: 884 across two files. 10 rows would need a decision:
3 application-ID conflicts, 2 unresolved person matches, 1 conflicting person ID,
4 workers not in Staff.

Proposal saved locally: <private-run>/preview/proposal.json
No Automation Log row was created, and no documents were attached.

Run it again as an apply when the proposal looks right.
```

Every number here is a proposal. The words "created" and "updated" are deliberately
absent, because nothing has been created or updated.

## A failed run

```text
Mode: Apply. The sync stopped before writing anything. The source CSV has no
`Binti application id` column, so no row could be matched to an Airtable
Application. No records were created or updated.

The log row is Failed and holds the details:
https://airtable.com/appExample01/tblLog01/viwLog01/recLogExample

Next step: re-export the applicant dashboard with the identifier column
included, then run the sync again.
```

No applicant names, no row-level detail, and no stack traces in chat. Those belong in the client documents and the log row.
