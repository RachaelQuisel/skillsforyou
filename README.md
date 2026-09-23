# Skills for you

Practical AI skills from Rachael Quisel. Take what helps, tweak it for your setup, and make it your own.

[Browse the skills](#available-skills) · [Get started](#get-started) · [Suggest a skill](https://github.com/RachaelQuisel/skillsforyou/issues/new?template=skill_request.yml) · [MIT license](LICENSE)

## Available skills

| Skill | What it does | Download |
| --- | --- | --- |
| [Dissonance Radar](dissonance-radar/SKILL.md) | Reviews conversations for missed questions, conflicting expectations, and changes worth asking about. Returns a few questions grounded in the transcript. | [ZIP](https://github.com/RachaelQuisel/skillsforyou/raw/refs/heads/main/downloads/dissonance-radar.zip) |
| [Gem Miner](gem-miner/SKILL.md) | Finds funny, sweet, weird, and memorable things you said, with exact quotes and source details for review. | [ZIP](https://github.com/RachaelQuisel/skillsforyou/raw/refs/heads/main/downloads/gem-miner.zip) |

## Get started

1. Download a skill ZIP and extract it, or clone this repository.
2. Open the skill's `SKILL.md`. Keep its supporting folders with it.
3. Use your assistant's supported skill installation or import process. If you're using an ordinary chat, attach `SKILL.md` and the relevant reference files along with your input.
4. Ask for the skill by name and give it the material to work with.

```sh
git clone https://github.com/RachaelQuisel/skillsforyou.git
```

You'll likely need to tweak the instructions for your LLM and system. Installation paths, tool names, file access, and invocation syntax differ between assistants.

## Try Dissonance Radar

```text
Use Dissonance Radar on this transcript. What questions did I miss asking?
For each question, show the exact excerpt that prompted it and explain
what decision the answer could change. Don't invent a problem to fill a list.
```

For a comparison:

```text
Use Dissonance Radar to compare these two meetings. What changed in
priorities, roles, commitments, or language? Cite both meetings when
you describe a change. Keep different clients' information separate.
```

See a [fictional transcript and sample review](dissonance-radar/examples/sample-review.md).

### What to expect

- A short, ranked set of questions, each tied to evidence.
- A practical next move, such as raising a question at the next meeting.
- Clear limits when context is missing. No findings is a valid result.

This public version works with material you supply or explicitly authorize it to read. It doesn't require Airtable, Slack, or a scheduled automation. It doesn't send messages or set up a monitor.

Share only conversation material you're authorized to use. Choose an assistant and data-handling setup appropriate for that material. Don't put private transcripts in public GitHub issues.

## Try Gem Miner

```text
Use Gem Miner on these messages. Find the funny, sweet, weird, or
surprising things I said. Keep the wording exact, include the source,
and return a short list for me to review. Don't publish anything.
```

It separates your own messages from other speakers, keeps quoted text separate from optional captions, and can return structured JSON if you request it. A quiet batch can produce no gems.

See a [fictional message batch and sample picks](gem-miner/examples/sample-gems.md). The public version works from supplied or explicitly authorized messages. It doesn't include private history extractors, Airtable credentials, or automatic uploads.

## How this repository is organized

```text
dissonance-radar/
  SKILL.md                 The skill's instructions
  agents/openai.yaml       Optional Codex display metadata
  references/lenses.md     Patterns to look for and evidence limits
  examples/sample-review.md
gem-miner/
  SKILL.md                 Quote-selection and output instructions
  agents/openai.yaml       Optional Codex display metadata
  examples/sample-gems.md
downloads/                 Installable ZIPs
scripts/package_skills.py  Rebuilds the ZIPs from source
```

The skill folders are the source of truth. ZIPs contain those same files plus the repository's license.

## More Airtable resources

The [Airtable AI Webinar repository](https://github.com/RachaelQuisel/Airtable-AI-Webinar) includes Questwood's source code, its original Omni prompt, the Omni Prompt Generator and Airtable Omni Custom Interface Refiner skills, speaker notes, and demo video links.

## Contribute

Found an instruction that doesn't work in your setup? [Open an issue](https://github.com/RachaelQuisel/skillsforyou/issues/new?template=bug_report.yml) with the assistant you used, what you expected, and a small anonymized example.

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes and new-skill proposals.

## License

[MIT](LICENSE). Keep the license and any applicable attribution when sharing adaptations.
