# Client vision and scope

## Trigger

I use this skill to agree on the problem, intended result, and boundaries before a build expands beyond what was decided.

A project needs a new or revised scope document.

## Inputs

- The project and build name.
- The problem, affected users, and intended outcome.
- Included work, exclusions, and unresolved boundary decisions.

## What happens

1. Confirm the project context.
2. Ask focused questions about the problem and desired result.
3. Describe the proposed vision in plain English.
4. List the included work and explicit non-goals.
5. Record boundary decisions that still need an answer.
6. Save or revise the local document.

## Outputs

A `vision-and-scope.md` file centered on the problem, vision, in-scope work, and out-of-scope work.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use client-doc-vision-and-scope for a fictional equipment-booking pilot. Include reservations and approvals. Exclude payments and equipment purchasing.
```

## Setup and limits

The document should not turn unanswered questions into commitments. Technical implementation detail belongs in the appropriate design document. GitHub publication is separate. Supply the intended local output folder.
