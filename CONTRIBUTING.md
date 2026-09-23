# Contributing

Useful skills solve a specific problem without depending on the author's private setup.

## Propose a skill

[Open a skill request](https://github.com/RachaelQuisel/skillsforyou/issues/new?template=skill_request.yml) and describe:

- The task someone wants to complete.
- The input they would supply.
- What a useful result would look like.
- Any tools or accounts it really needs.

## Improve an existing skill

1. Fork the repository and make a focused change.
2. Explain the real problem the change addresses.
3. Try the instructions with a small fictional or anonymized example.
4. Include the result and any limitations in your pull request.

Don't add private transcripts, client names, account identifiers, credentials, or personal file paths. Use invented examples and label them as such.

## Folder conventions

- Use a lowercase, hyphenated folder name.
- Put `name` and `description` in YAML frontmatter at the top of `SKILL.md`.
- Keep supporting references and examples in the skill folder, linked from `SKILL.md` when needed.
- Say what input is needed and what output the user should expect.
- Make integrations optional unless the skill genuinely requires them.
- Preserve attribution and applicable licenses.
- Update the root skill index when adding a skill.

## Rebuild downloads

From the repository root, run:

```sh
python3 scripts/package_skills.py
```

This uses Python's standard library to rebuild ZIPs for the top-level skill folders. Commit the updated ZIP alongside its source changes. Each ZIP includes the repository license.

## Report a problem

Use the [bug report form](https://github.com/RachaelQuisel/skillsforyou/issues/new?template=bug_report.yml). Include your assistant, the skill, the observed result, and an anonymized reproduction. A small example is more useful than a private transcript dump.
