# Postmortem

## Trigger

I use this skill to ask consistent monthly reflection questions across active projects. It keeps the prompt short and checks whether it was already posted.

A monthly reflection needs to be previewed, sent, audited, or scheduled.

## Inputs

- The reporting month and configured time zone.
- Active project records and authoritative Slack routing.
- The question bank and access to channel history.

## What happens

1. Choose preview, send, audit, or schedule mode.
2. Find eligible projects and resolve one internal destination per client.
3. Select three relevant questions from the included question bank.
4. Check channel history for the same monthly header.
5. Skip existing posts and unresolved destinations.
6. Send only in an explicitly authorized send run.
7. Report posted, already posted, missing-routing, ambiguous-routing, and failed results.

## Outputs

A preview, an audit report, or authorized monthly reflection posts with per-destination results.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use postmortem in preview mode for a fictional active-project roster. Show the routing and three questions. Do not post messages.
```

## Setup and limits

Preview is the default. Missing channel history blocks sending because duplicate checks cannot be completed. Scheduling is handled by the host product. The included public question bank is a generic replacement. Supply your own review questions when needed.
