---
name: slack-power-map
version: 1.0.0
description: Compare formal reporting lines with observed collaboration and routing patterns in a permitted, de-identified Slack sample. Includes a synthetic example and an offline summary script.
---

# Slack Power Map

Use this skill to investigate questions such as which teams are asked for help, which decisions wait for a handoff, or which teams are missing from a process. Treat the observations as a starting point for questions, not as a ranking of people or proof of authority.

## Set the scope

Ask for the question, date range, approved channels, and a supplied org chart if one is available. Do not infer reporting lines from Slack titles, membership, or administrator privileges. Distinguish the stated reporting structure from observed work patterns. If no chart is supplied, say so.

Use the included fictional example first. For real work, use the smallest authorized sample and a local, approved environment. Do not read direct messages, private channels, or personal information for this workflow. Do not collect messages automatically, request credentials, or copy workplace data to GitHub or an unapproved service. Use aliases and remove free-text messages, names, links, exact times, and other identifying details from the working sample. Aliases do not make real data anonymous; combinations of team, role, and activity can still identify someone.

## Count and interpret

Assign a single category to each distinct, reviewed event: a request, a handoff, or an explicitly recorded decision. Direction goes from the originating team to the receiving team. Use pseudonymous team identifiers; do not publish individual scores. Count internal and cross-team events separately. Treat small counts as insufficient evidence and apply approved privacy thresholds to all shared summaries.

For each observation, report the count, range, scope, one possible alternative explanation, and one question to verify with the process owner. Compare with the supplied chart without assuming the two should have the same shape. High activity may reflect support duties, or simply which channels were sampled. Low activity is not proof that someone was uninvolved. Document missing channels, offline decisions, specialists with assigned routing duties, and uneven participation or time zone coverage. Keep any authorized evidence references private.

Do not use the report for performance evaluation, promotion, discipline, employment decisions, or assertions about personal influence. Review proposed sharing with the data owner before distributing findings.

## Try the included example

From the skill folder, run:
```sh
python3 scripts/summarize.py examples/synthetic-events.json
```

The script only reads the supplied local file and writes aggregate counts to standard output. See [the guide](README.md) for the input format and expected result.
