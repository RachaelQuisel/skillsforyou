# Write artifact

## Trigger

I use this skill to save a finished report as a structured Airtable record so it can be found alongside the relevant project.

A completed document needs to be stored in the configured Artifacts table.

## Inputs

- The project and destination base.
- The title, body, document type, reporting period, and dates.
- Optional project links and approval of the content.

## What happens

1. Resolve the configured destination.
2. Prepare the record fields from the supplied document.
3. Show the content for confirmation.
4. Create a new record with Draft status after approval.
5. Include approved project links when provided.

## Outputs

A new document record in Airtable when the write succeeds.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use write-artifact to prepare a fictional monthly inventory report for storage. Show the title, dates, type, and body before creating the record.
```

## Setup and limits

The source workflow is additive. It does not overwrite existing records. It requires the destination base, table, and field mapping. Validate select values before writing. Read back the created record to verify the content.
