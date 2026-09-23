# Airtable backup

## Trigger

I use this tool to save a local copy of an Airtable base before making changes. The package is named `airtable-backup-and-migrate`, but this version only creates backups. Restore and migration are not implemented.

Run it when you need a snapshot of a base's data and structure.

## Inputs

- Python 3.10 or later. No additional Python packages are required.
- The source base ID.
- A file containing an Airtable personal access token with record-read and schema-read access to that base.
- An output directory with enough free disk space.

## What happens

1. The script checks the available disk space.
2. It reads the base schema and retrieves the table records.
3. It saves record values using field IDs so display-name changes do not change the keys.
4. Unless attachments are skipped, it downloads their files to local storage.
5. It records counts and the completion or failure state in a manifest.

The source base is read-only during the backup. Keep the token file and backup data outside the public repository.

## Outputs

Each run creates a timestamped directory:

```text
schema.json
records/
  <table-id>.json
attachments/
  <table-id>/<record-id>/<filename>
MANIFEST.json
```

Attachment files are saved locally because remote attachment links expire. The manifest describes the run. Its presence alone does not prove that every part of the backup succeeded.

## Run it

From the directory containing `backup.py`:

```bash
python3 backup.py \
  --base-id appXXXXXXXXXXXXXX \
  --pat-path /path/outside/repository/airtable-token \
  --out-dir /path/outside/repository/backups
```

Replace the placeholder values with your own configuration. The token file should contain only the token.

Add `--skip-attachments` to save schema and records without downloading attachment files. Use `--min-free-gb 10` to require at least 10 GiB of free space before starting.

## Check the result

A successful run exits with code `0` and prints a line beginning with `BACKUP OK:`. Review the manifest and any reported errors. Treat a missing manifest or a nonzero exit code as an incomplete backup.

## Limits

- The tool does not restore data.
- It does not back up interfaces, automations, views, collaborator permissions, or sync configuration.
- It does not resume interrupted runs or write files atomically.
- It does not calculate a checksum for each saved file.

## Fictional example

Before changing fields in a sample equipment inventory, create a backup and check its result. Keep that snapshot separate from the working data. A recovery plan still needs a tested restore process.
