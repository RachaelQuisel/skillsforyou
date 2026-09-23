# Client document changelog

## Trigger

I use this skill to record what shipped and what changed for the people using it.

A completed change needs a dated entry in the project changelog.

## Inputs

- The project and build name.
- The shipped change and its user-visible effect.
- The existing changelog, when one exists.

## What happens

1. Confirm the project and build.
2. Capture what shipped and what changed for the user.
3. Read the existing file.
4. Add a new date at the top or append under the matching date.
5. Preserve the earlier entries and verify placement.

## Outputs

An updated local `changelog.md` file.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use client-doc-changelog for a fictional reservation system. The cancellation form is now live, and users can release equipment without emailing support.
```

## Setup and limits

The changelog records shipped work. Drafts and planned changes belong elsewhere. This skill writes locally; GitHub publication is a separate action through client-doc-push. Supply the local project folder before saving.
