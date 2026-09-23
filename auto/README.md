# Auto

## Trigger

I use this skill to write a short explanation of one automation from its actual source.

An automation needs a concise operating explanation or its current documentation needs an update.

## Inputs

- The exact automation and project.
- Current source code or live configuration.
- Existing documents that describe the same workflow.
- For Airtable, access to the required read-only tooling.

## What happens

1. Identify the automation without guessing from an ambiguous name.
2. Read its source and existing documentation.
3. For Airtable-native workflows, use authorized read-only tooling to capture the live definition.
4. Describe the trigger, inputs, actions, conditions, and outputs.
5. Flag unknown script effects or unresolved references.
6. Save the explanation and supporting evidence.
7. Update directly related documentation when it is now inaccurate.

## Outputs

A concise education document. Live Airtable runs also produce a source snapshot and post-run analysis.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use auto to explain this fictional equipment-reminder automation from the supplied source. Include its conditions and failure route. Label anything the source does not establish.
```

## Setup and limits

This public version is a documentation workflow. It does not include the private automation reader. Use source files or compatible read-only tooling available in your environment. A local sample is not proof of a live read. The post-run analysis must support any claim that the source was verified live. Draft-only requests should not change project files.
