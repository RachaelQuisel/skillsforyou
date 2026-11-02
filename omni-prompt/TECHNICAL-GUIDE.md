# Omni prompt

## Trigger

I use this skill to write Airtable prompts with explicit inputs, a clear output format, and instructions for missing data.

An AI field, interface, or other Omni build instruction needs a new or revised prompt.

## Inputs

- The intended task and audience.
- Verified field and table names, or clearly labeled proposed names.
- The required output type, format, and missing-data behavior.

## What happens

1. Identify whether the request is for an AI field or an interface change.
2. Verify relevant schema names when an existing base is involved.
3. Define the assistant’s role and explain how each input is used.
4. Number the required results and state the format limits.
5. Specify what to do when the input is blank or ambiguous.
6. Return self-contained prompt blocks.

## Outputs

Copy-pasteable prompts. AI field blocks include Field name, Custom instructions, Input fields, Output field type, and Model.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use omni-prompt to draft an AI field prompt for a fictional maintenance request. Use {Request description} and {Requested date}. Do not infer a deadline when none is given.
```

## Setup and limits

Drafting a prompt does not run it or authorize changes to a base. Model selection and current product capabilities need verification when they affect the prompt. Historical capability notes in the source package should not be treated as current product documentation.
