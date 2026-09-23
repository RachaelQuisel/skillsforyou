# Evaluation creation

## Trigger

I use this skill to turn “does this work?” into a small set of questions someone can answer with evidence. An evaluation is a defined way to check whether a process achieved its goal.

Use this skill when a repeated task needs success criteria, a definition of done, or rules for handling failed runs.

## Inputs

- The outcome the user needs.
- Examples of completed work and known failures, when available.
- Rules with an exact expected result.
- Someone who can judge the parts that require domain knowledge.

## What happens

1. The assistant states the goal in one sentence.
2. It reviews available examples and identifies meaningful failures.
3. It writes a separate pass-or-fail question for each important check.
4. It assigns exact checks to simple rules or code.
5. It leaves judgment calls with a knowledgeable person unless an AI reviewer has been checked against human decisions.
6. It defines success, completion, stop conditions, and the response to failure.

If real examples are unavailable, the evaluation identifies that gap. It uses the stated requirements without presenting imagined failures as observed evidence.

## Outputs

A short evaluation with these sections:

- Purpose.
- Evidence reviewed.
- What to check.
- What success looks like.
- When the work is done.
- When to stop.
- What to do after a failed run.
- Final result.

## Try it

Load `SKILL.md` in your assistant, then supply the workflow and examples:

```text
Use eval-creation for a weekly inventory report.
The report should include every active product exactly once.
Its quantities must match the source export.
I will provide three reports and the errors found during review.
Write the checks in plain English and identify any missing evidence.
```

## Fictional example

For that inventory report, two exact checks would be:

- Does each active product appear exactly once?
- Does each reported quantity match the source export?

A person would review whether the explanation of stock shortages is useful. That judgment needs clear examples before an AI reviewer can be trusted to make it.

## Limits and attribution

This skill writes an evaluation. It does not supply a test runner or prove that a workflow passed.

Its retry rule allows no more than ten complete attempts. It requires a correction before retrying and an earlier stop when continuing could cause harm.

The approach draws on Hamel Husain's published evaluation practices. The package's `references/hamel-husain-evaluation-practices.md` contains the source list. Credit for the underlying methodology belongs with those sources.
