# Modes, writer checks, and delivery

Run commands from the current project. The Python runner uses that project's reconciliation engine. Do not copy the engine into this skill.

`<config>` below is the path to your destination configuration, described in [config.md](config.md).

## Audit and Preview

Use Audit for read-only investigation. The runner's Audit command checks local configuration and the local runner lock. It does not prove that an external writer is inactive:

```sh
python3 scripts/run_applicant_airtable_sync.py --mode audit
```

Preview each supplied source without Airtable writes:

```sh
python3 scripts/run_applicant_airtable_sync.py \
  --mode preview \
  --csv <source.csv> \
  --output-dir <private-run-directory>/<source-key> \
  --all-source-applications \
  --source-wins
```

The command-line default is Preview. Use an explicit mode in skill runs. Use a fresh output folder for each attempt. Never reuse a folder that contains write receipts. Keep Preview files local. Do not call either Airtable log helper in Audit or Preview.

## Verify active writers before Apply

1. Read the current Automation Inventory entry and relevant recent logs. Inspect available Airtable trigger configuration, project workflows, schedules, and current runner code. Use the live surfaces available to this task.
2. Determine which writers can change these mapped tables and fields during the import. Distinguish configured triggers from observed running jobs. An inventory status or old document alone does not prove runtime state.
3. If an overlapping writer is active or cannot be checked, stop Apply. Report the evidence gap. Do not disable triggers, change schedules, or deploy a replacement writer without explicit authorization.
4. Save a private writer-check JSON file only after the check supports no overlapping external writer. Include the target base, this writer's ID, a UTC check time, no active overlapping writers, and sanitized evidence sources. Never invent an observation to satisfy the file contract.

```json
{
  "baseId": "appXXXXXXXXXXXXXX",
  "writerId": "applicant-csv-import",
  "checkedAt": "<ISO-8601 UTC time>",
  "activeWriters": [],
  "evidence": ["<current sanitized source or link and its observed result>"]
}
```

The check expires after 30 minutes. Refresh it from current evidence before continuing. The runner validates it again before business writes. The runner's operating-system lock serializes imports through this runner for this base. It does not lock Airtable automations, other scripts, or external services.

## Apply and log

After intake, Preview, and the writer check pass, create one Automation Log. Use one stable run key for every source and retry:

```sh
python3 scripts/log_sync_run.py \
  --config <config> \
  --run-key <run-key> \
  --outcome Failed \
  --fields-written "No business records have been changed yet." \
  --notes "The sync is running. The final result is pending." \
  --reason "The sync has not finished." \
  --duration-ms 0
```

Starting at `Failed` means an interrupted run never looks successful.

Apply each source once. Use separate private output folders and the same confirmed log link:

```sh
python3 scripts/run_applicant_airtable_sync.py \
  --mode apply \
  --writer-check-file <private-writer-check.json> \
  --csv <source.csv> \
  --output-dir <private-run-directory>/<source-key> \
  --diff-csv-output <client-document-directory>/<source-name>-airtable-diff.csv \
  --automation-log-url <automation-log-record-url> \
  --all-source-applications \
  --source-wins
```

A legacy `--apply` flag also requires a valid writer-check file. Never bypass the gate through an underlying command.

## Finish and deliver

Keep the log Failed while preparing and attaching reports. After delivery verification, call `log_sync_run.py` with the same run key, final outcome, source organizations, confirmed counts, elapsed time, and a plain-English note. Do not create a second row.

- Use `Succeeded` only after readback finds no pending valid writes, retained source differences, identity conflicts, or unresolved source worker links, and every requested client attachment is verified.
- Use `Failed` for blocked writes, partial writes, unresolved rows, or incomplete delivery. State which valid changes completed.
- Use `Skipped` only when a completed comparison confirms no eligible work and the required report delivery is verified. Do not use Skipped to hide unknowns or unresolved rows.

Attach the current annotated CSVs, report, field-level changes CSV, and review CSV:

```sh
python3 scripts/attach_log_documents.py \
  --config <config> \
  --run-key <run-key> \
  --docs-root <client-document-directory> \
  --documents <source-diff.csv> <client-report.md> <field-changes.csv> <review-items.csv>
```

Include every source diff when there are multiple files. The helper verifies filenames, byte sizes, and downloaded SHA-256 digests. Keep exactly the current client document set. Keep the sharing archive local. On failure, attach available documents and retain Failed. Never claim delivery from an accepted upload request alone.
