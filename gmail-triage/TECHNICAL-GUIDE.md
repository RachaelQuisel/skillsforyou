# Gmail triage

## Trigger

I use this skill to separate messages that need a decision from mail that can be filed or answered with a draft.

An authorized inbox review is requested.

## Inputs

- Access to the selected Gmail account.
- Approved sender rules and existing labels.
- Prior action history and drafting preferences.

## What happens

1. Read the available labels and recent triage history.
2. Find messages in the selected scope.
3. Apply configured sender rules.
4. Classify mail for filing, drafting, personal review, or sponsorship handling.
5. Prepare noncommittal replies as drafts.
6. Apply labels and archive messages according to the rules.
7. Record actions and report the messages needing attention.

## Outputs

An organized inbox, saved reply drafts, an action log, and a short report.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Using only these fictional email summaries, demonstrate gmail-triage classifications. Do not connect to an inbox, change labels, archive mail, or create drafts.
```

## Setup and limits

The installed workflow changes mailbox state. It does not send the prepared replies. The package contains no sender addresses or personal routing. Supply your own classification rules and scope. Requests involving commitments require human review under the source rules.
