# Gem Miner

## Trigger

I use Gem Miner to find memorable lines in messages I supply or explicitly authorize the assistant to read.

## Inputs

- Supply a message batch and identify the speaker whose words should be reviewed.
- Include timestamps or source references when available.

## What happens

1. The assistant reviews only the authorized material.
2. It selects a small set of memorable lines and preserves the exact wording.
3. It separates quotes from optional captions.
4. It excludes sensitive disclosures and checks for duplicate selections.

## Outputs

- Each candidate includes its quote, source, category, and a short reason for selection.
- No qualifying messages is a valid result.

## Try it

```text
Use Gem Miner on this fictional message batch. Keep quotes exact and return candidates for review. Do not publish or upload anything.
```

See the [fictional example](examples/sample-gems.md).

## Limits

This public version includes no private history reader, credentials, automatic upload, or publishing integration. It returns material for review. The user chooses whether to share it.
