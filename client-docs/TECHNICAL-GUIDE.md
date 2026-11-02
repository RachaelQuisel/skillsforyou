# Client documentation

## Trigger

I use this skill to keep the main project documents consistent as the work changes.

A build needs documentation updates or missing project documents need to be identified.

## Inputs

- The selected project and build.
- Existing repository documents.
- Verified decisions, delivered changes, plans, and measurements.
- Access to the configured task service and GitHub repository.

## What happens

1. Resolve the project directory without creating a duplicate.
2. Read the existing document set.
3. Match each change to the document that owns that information.
4. Preserve decision history and dated shipment entries.
5. Use explicit empty sections when information has not been captured.
6. Update approved repository files through the GitHub API.
7. Report the files changed.

## Outputs

A maintained set of eight files: `prd.md`, `vision-and-scope.md`, `build-plan.md`, `kpi-report.md`, `interface-prompts.md`, `user-stories.md`, `decisions.md`, and `changelog.md`.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use client-docs to review a fictional project’s eight-document set. Identify which documents need updates from the supplied notes. Return a proposed change list before repository writes.
```

## Setup and limits

This coordinating skill can write directly to GitHub. The individual document skills generally stage local files. Configure both paths deliberately. Supply an authorized task source and repository. Do not infer either from another installation. Review internal planning material before including it in a client-readable set.
