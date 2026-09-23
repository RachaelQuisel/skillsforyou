# Reconciliation Artifact Templates

## Before-state evidence

```markdown
# [Project] Pain Point Before-State

Captured: [ISO timestamp]
Base/table: [IDs and names]

| Record ID | Name | Status | Time | Last Modified | Notes hash | Definition hash | Consultant Updates hash | Response hash |
|---|---|---|---:|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

Mutable field IDs: [list]
Protected field IDs: [list]
```

Hash long text with SHA-256 over the exact UTF-8 value. Record null separately from an empty string.

## Evidence record

```markdown
## [Pain Point]

- Record: [record ID]
- Work completed: [specific change]
- Configuration proof: [automation/action/version/hash]
- Test proof: [command and result]
- Operational proof: [run/log/delivery/destination record]
- Evidence boundary: [what is still not proven]
- Status decision: [before → after or preserved]
```

## Update manifest document

```markdown
| Record | Current status | Proposed status | Mutable fields | Evidence threshold and decision |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

### Exact Consultant Updates value

[YYYY-MM-DD — What changed. Strongest proof. Remaining gap. Status decision.]
```

## Verifier JSON

The before and after files may be a normalized record object or a raw array:

```json
{
  "records": [
    {
      "id": "recExample",
      "fields": {
        "fldStatus": "New",
        "fldUpdates": null,
        "fldNotes": "Protected text"
      }
    }
  ]
}
```

`cellValuesByFieldId` from Airtable is also accepted in place of `fields`.

The manifest contains only intended writes. Fields absent from a record's manifest entry are protected by default.
Every manifest must contain at least one intended field. Never list an intended field in `ignoredFieldIds`.

```json
{
  "ignoredFieldIds": ["fldLastModified"],
  "allowTrailingNewlineFieldIds": ["fldUpdates"],
  "appendFieldIds": ["fldUpdates"],
  "records": [
    {
      "id": "recExample",
      "fields": {
        "fldStatus": "In Progress",
        "fldUpdates": "2026-09-10 — Implemented and verified. Live-event proof remains pending."
      }
    }
  ]
}
```

Ignore only system-managed or computed fields that are expected to recalculate. List each ignored field ID explicitly in the evidence document.

`appendFieldIds` makes the verifier prove that any prior field value remains an exact prefix of the new value and that new text follows it after a blank line. Use it for `Consultant Updates` and any other append-only history field.

## Change log

```markdown
# [Project] Pain Point Change Log

Executed: [ISO timestamp]

## Outcome
- [Count] records updated.
- [Count] statuses advanced.
- [Count] records closed.

## Record decisions
| Record | Before | After | Proof | Remaining gap |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Integrity verification
- Verifier result: PASS.
- Protected fields changed: 0.
- Time values: [preserved or explicitly approved changes].
- Mutation IDs: [IDs or not exposed].
```
