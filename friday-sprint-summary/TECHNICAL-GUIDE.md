# Friday sprint summary

## Trigger

I use this workflow to produce a consistent weekly update from current task data and supporting project records.

An authorized weekly run is requested or a configured schedule starts it.

## Inputs

- The reporting window and project roster.
- Current task records and configured project tags.
- Verified Slack destinations.
- Recent transcripts and local artifacts when available.

## What happens

1. Calculate the reporting window.
2. Read task data and group completed, active, and carried work.
3. Apply the configured tags and calculate the summary metrics.
4. Review recent artifacts for work missing from the task list.
5. When a supporting report is requested, prepare it from authorized recent material.
6. In dry-run mode, save the run log and show drafts without posting or creating a Slack Canvas.
7. In authorized send mode, deliver the updates and report failures.

## Outputs

Weekly sprint updates, a run log, and an optional linked supporting report.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use friday-sprint-summary in dry-run mode for a fictional project roster. Show the drafts and any missing source data. Do not send posts or create a Slack Canvas.
```

## Setup and limits

This public version defaults to a dry run. It includes no schedule, routing, or standing send permission. The standalone KPI report is internal by default, so its content needs an audience review before external sharing.
