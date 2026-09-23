# Client interface prompt documentation

## Trigger

I use this skill to keep the prompt and iteration history behind a generated interface available for the next person who works on it.

An interface-building prompt needs to be captured or updated in the project record.

## Inputs

- The project, app name, and exact prompt.
- The intended features, data model, appearance, and behavior.
- Iteration notes and errors returned during the build.

## What happens

1. Confirm the app and project.
2. Capture the purpose and intended users.
3. Document the features and data requirements.
4. Preserve the exact prompt in a dated app section.
5. Record revisions and errors without inventing a build history.
6. Save the local documentation file.

## Outputs

An `interface-prompts.md` file with a dated section for each documented app.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use client-doc-interface-prompts to document this fictional equipment-dashboard prompt and the two supplied revisions. Preserve the prompt text exactly.
```

## Setup and limits

Record the builder and version used when known. Do not infer current product capabilities from an old prompt. This workflow documents prompts; it does not prove that an app was built or published. GitHub publication is separate.
