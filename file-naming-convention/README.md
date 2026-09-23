# File naming convention

## Trigger

I use one filename pattern to make project documents easier to find. The name tells me which project a file belongs to, what it contains, and when it was created.

A project document needs to be saved or an unclear filename needs to be replaced.

## Inputs

- The project code and document type.
- The relevant date, topic, and version when needed.
- The existing folder structure.

## What happens

1. Choose the project code and document type.
2. Use the document date or the date of the event it describes.
3. Add a topic only when it helps distinguish the file.
4. Add a version when another version exists.
5. Save the file in the established folder and preserve earlier versions when needed.

## Outputs

A filename in the form `<PROJECT>-<Type>-YYYY-MM-DD[-topic][-v2].ext`.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use file-naming-convention to name a fictional Northwind workshop recap from September 10, 2026. Use NW as the project code.
```

## Setup and limits

The source convention applies to project documents. It excludes code, configuration, temporary files, and unrelated folders. A sample result is `NW-CallNotes-2026-09-10-Workshop.md`. Choose project codes and folders for your own workspace.
