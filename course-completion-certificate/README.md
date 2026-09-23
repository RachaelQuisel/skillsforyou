# Course completion certificate

## Trigger

I use this workflow to create or retrieve a completion certificate for one clearly identified student.

A user asks to create, retrieve, replace, or verify a course completion certificate.

## Inputs

- The selected student and requested action.
- The current student and grade records.
- The certificate template and configured Airtable fields.
- The PDF tools required by the supplied template.

## What happens

1. Ask which student to use when no student is identified.
2. Resolve exactly one student record.
3. Inspect eligibility and any existing certificate.
4. Ask for a decision when an existing certificate or eligibility exception requires one.
5. Use the supplied certificate template and available PDF tooling for an authorized creation.
6. Attach the file, record the result, and verify the stored certificate.
7. Return the relevant file or record link and any unresolved notes.

## Outputs

A certificate PDF and its verified destination record, or a clear explanation of what prevents completion.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Using a fictional student record, demonstrate the course-completion-certificate workflow in review-only mode. Explain the required checks without generating or attaching a real certificate.
```

## Setup and limits

This public version is a workflow guide. It does not include a certificate template, institution-specific eligibility rules, or a generation script. Supply those for your own course. If an attachment write is uncertain, read the destination before retrying and report any unresolved duplicate risk.
