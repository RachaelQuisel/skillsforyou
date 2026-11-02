# Normalize CSVs for Airtable

## Trigger

I use this skill when several spreadsheets need to become one reliable Airtable import. It preserves source values and makes uncertain records visible for review.

Use it when source CSV files have different column layouts, inconsistent formatting, or values that need to match an existing Airtable base.

## Inputs

- The source CSV files.
- Read access to the destination schema.
- Known lookup values, such as approved categories.
- A decision about the shape of the destination data.

The data can be wide, with related events in columns on one row. It can also be long, with one row per event. The choice depends on how people need to use it.

## What happens

1. The assistant inventories the files and identifies differences between their columns.
2. It reads the destination schema before proposing fields or links.
3. It drafts the target schema and normalization rules for approval.
4. It writes a source-specific normalizer using the approved schema and rules.
5. It preserves raw values and records any approved corrections.
6. It flags uncertain values and possible duplicates for human review.
7. It prepares the import files and a migration assessment.
8. After import, it compares record counts and checks source rows against Airtable.
9. If fields were lost during import, it prepares a targeted update using tracking IDs.

Names stay unchanged unless a correction is explicitly approved. Duplicate records are flagged rather than removed automatically.

## Outputs

- One combined CSV with source-file references, source-row numbers, tracking IDs, review status, and review reasons.
- A change file recording automatic corrections.
- A summary of counts and review categories.
- A README for the adapted script.
- An assessment explaining decisions, unexpected findings, and unresolved questions.

## Try it

Load `SKILL.md` in an assistant with file access and permission to read the destination schema:

```text
Use normalize-csvs-for-airtable for these three fictional equipment-checkout exports.
Keep all source values available for comparison.
Show me the proposed schema and correction rules before writing the normalizer.
Flag possible duplicates without deleting them.
```

This public package provides the workflow rather than a universal converter. The assistant must write and validate a normalizer for the supplied files.

## Fictional example

One export uses `Checkout Date`. Another uses `Date Out`. Both map to the approved destination field. A row with an unknown equipment category stays in the output with a review reason.

## Limits

A generated CSV is not proof of a successful Airtable import. The workflow requires a record-count comparison and ten source-to-destination spot checks. Those spot checks are a sample, not a comparison of every field in every row.
