# Mistakes

## Trigger

I use this skill to review an assistant’s work against the actual request. A useful correction explains the error, its consequence, and how to avoid repeating it.

An answer, plan, file, action, or completion claim needs an evidence-based review.

## Inputs

- The original request and the work delivered.
- Relevant source material, conversation history, files, and tool results.

## What happens

1. Set the review scope.
2. Reconstruct what was requested, promised, and done.
3. Compare the result with the requirements and available evidence.
4. Describe each supported mistake and its practical effect.
5. Give the correction and a specific prevention rule.
6. Correct authorized work and identify anything still unresolved.

## Outputs

A focused review of substantiated mistakes, corrections, prevention rules, and remaining unknowns.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use mistakes to review this fictional migration report against its source totals. Check whether the completion claim is supported.
```

## Setup and limits

The skill should not invent faults to fill a report. If the evidence is unavailable, the finding stays uncertain. It is a review workflow, not an independent guarantee that the assistant will catch every error.
