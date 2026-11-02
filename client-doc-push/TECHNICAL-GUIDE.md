# Client document publishing

## Trigger

I use this skill to publish a reviewed set of project documents to the correct GitHub location.

Local project documents have been staged and the user explicitly authorizes publication.

## Inputs

- The approved documents and verified repository destination.
- Authenticated GitHub access with write permission.
- The existing remote file versions and correct project directory.

## What happens

1. Inspect the staged Markdown files.
2. Check that the remote project directory is the intended destination.
3. Limit publication to the supported document set.
4. Show the proposed publication scope and obtain the required approval.
5. Read current remote file versions.
6. Create or update the files through the GitHub API.
7. Report which files were published.

## Outputs

GitHub commits for the approved files and a report of the publication result.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use client-doc-push to inspect a fictional staged documentation set. Show the proposed destination and file list. Stop before publication.
```

## Setup and limits

The supported set contains the PRD, vision and scope, build plan, KPI report, interface prompts, user stories, decisions, and changelog. Supply the repository, branch, and staging directory. No private destination is bundled. This README does not authorize a push, and local files alone are not evidence of publication.
