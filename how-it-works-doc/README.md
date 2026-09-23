# How-it-works document

## Trigger

I use this skill to explain an automation in terms of the person who operates it. The document should make the trigger, result, and limits easy to follow.

A workflow needs an explanation for an operator, owner, or engineer.

## Inputs

- The automation’s name and source code or configuration.
- The intended reader.
- Existing documentation and the correct project folder.

## What happens

1. Read the implementation before describing its behavior.
2. Identify the trigger and required inputs.
3. Describe the actions in order.
4. Explain the outputs and the workflow’s boundaries.
5. Add operational detail where the automation is complex.
6. Save the document beside the code or in the established documentation folder.

## Outputs

A Markdown file named `HOW-IT-WORKS-<automation-slug>.md`.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use how-it-works-doc for this fictional overdue-equipment reminder. Explain what starts it, which records it reads, what it sends, and what it leaves unchanged.
```

## Setup and limits

This skill documents a workflow; it does not deploy or test it by itself. It is different from a code walkthrough or a base-wide automation inventory. Supply the relevant source and audience. No private example documents are required.
