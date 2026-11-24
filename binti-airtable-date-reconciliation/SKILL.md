---
name: binti-airtable-date-reconciliation
version: 1.0.0
description: Preview differences between an authorized Binti export and Airtable application dates. Use for received-date or initial approval-date reconciliation. Read only by default.
---

# Reconcile application dates

Use a user-provided Binti export or a strictly scoped, authorized read-only source. Do not ask for credentials in chat, sign in as another person, or open a production portal by default. Ask for the relevant source columns, confirmation of which source event represents each date, authorized destination and field mapping, and time zone. Work locally with the minimum fields needed, not complete applicant files.

1. Identify each application by a stable, unique identifier shared by both sources. Do not use a name alone. If IDs are missing, duplicated, or disagree, leave the row unchanged and flag it for review.
2. Normalize explicit dates to the agreed time zone and compare calendar dates. Never infer an ambiguous date or clear a destination value because the source is blank. Apply received dates only to in-scope applications and approval dates only where the approved mapping applies.
3. Preview the exact proposed changes, unchanged count, and review cases. Use IDs rather than names in the amount of detail needed and do not include personal details in general reports. Do not create records, reassign staff, change statuses, or send notifications.
4. Only write if the user explicitly approves the preview and the exact destination and fields. Re-read target records first and skip any that changed since the preview. Change only approved fields, then read back the results. A repeat against unchanged inputs should propose no new edits.

## Synthetic preview

| Example ID | In-scope date | Source | Destination | Outcome |
| --- | --- | --- | --- | --- |
| DEMO-01 | Received | 2026-01-05 | Blank | Propose fill |
| DEMO-02 | Initial approval | 2025-08-12 | 2025-08-12 | No change |
| DEMO-03 | Received | 2026-01-08 | Two destination matches | Flag; no write |
| DEMO-04 | Received | Blank | 2026-01-07 | Keep existing date |

Use a sandbox and synthetic records to test mappings before an approved real run.
