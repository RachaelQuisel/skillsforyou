# Client document decisions

## Trigger

I use this skill to preserve why a decision was made so someone can understand it later without reopening the whole conversation.

A project decision needs to be recorded.

## Inputs

- The project and build name.
- The decision, its reason, and alternatives considered.
- The existing decision log.

## What happens

1. Confirm the scope.
2. Ask for missing decision context.
3. Read the current log.
4. Append a dated entry explaining the choice and rejected alternatives.
5. Preserve earlier entries, including decisions later reversed.

## Outputs

An updated local `decisions.md` file containing lightweight architecture decision records.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use client-doc-decisions for a fictional equipment service. Record the choice to require approval for high-value reservations, including the reason and the alternative considered.
```

## Setup and limits

A reversal becomes a new entry that references the earlier decision. The original history is not rewritten. Publication is handled separately. Supply the local destination. No repository mapping is bundled.
