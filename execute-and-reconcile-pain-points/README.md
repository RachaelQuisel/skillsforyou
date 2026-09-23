# Execute and reconcile pain points

## Trigger

I use this skill to keep issue records consistent with the work that has actually been verified. A pain point is a documented problem someone needs resolved.

Use this skill when approved implementation work also needs an update in the system that tracks the problem.

## Inputs

- The approved scope and any existing implementation plan.
- Access to the current implementation and the relevant issue records.
- The requirements for considering each issue resolved.
- The fields the assistant is allowed to change.

## What happens

1. The assistant identifies the correct project and reads its live schema and status options.
2. It matches the work to specific issue records.
3. It saves the current implementation state and record values before making changes.
4. It completes the approved work and gathers evidence of the result.
5. It proposes a status and progress update for each matched record.
6. If an issue changed after the initial read, it stops that update for review.
7. It applies authorized updates and reads the records again.
8. It checks the result against a manifest, which lists the exact intended changes.

The assistant preserves the original problem description and completion requirements unless changes to them were explicitly requested. It appends progress notes without replacing earlier entries. It does not invent time spent.

## Outputs

- A saved before-state and an exact update manifest.
- Evidence supporting each status decision.
- A verification result for the changed records.
- A change log with any unfinished requirements.

## Try it

Load `SKILL.md` in an assistant that can access the relevant project and record system. For example:

```text
Use execute-and-reconcile-pain-points for the approved duplicate-notification fix.
Check the matching issue's completion requirements.
Show the evidence for its status before updating it.
Preserve the original description and all earlier notes.
```

The verifier runs locally with Python 3:

```bash
python3 scripts/verify_reconciliation.py --self-test

python3 scripts/verify_reconciliation.py \
  --before before.json \
  --after after.json \
  --manifest manifest.json
```

Use the package's artifact templates to prepare the JSON files. A passing record comparison confirms that the supplied snapshots match the intended changes. Operational evidence is still required to show that the underlying fix worked.

## Fictional example

A reminder workflow has been deployed, but no scheduled run has occurred. The progress note records the deployment. The issue stays open until a real run satisfies its completion requirements.
