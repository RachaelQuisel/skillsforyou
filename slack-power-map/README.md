# Slack Power Map

Compare a formal organization chart with how work requests, handoffs, and recorded decisions move between teams in a defined Slack sample. The output tells you which patterns are worth investigating, not who has authority or how well someone performs.

This public edition includes a fully fictional dataset. No messages or identifiers were taken from a real Slack workspace. The example uses anonymous participant IDs and contains no message text, names, organization details, credentials, or links to actual conversations.

## Run the example

From this folder, run:

```sh
python3 scripts/summarize.py examples/synthetic-events.json
```

The sample has seven events: six between teams and one within a team. The most frequent cross-team path appears three times. The JSON output shows counts by direction and category, not individual rankings. The script requires Python 3 and has no network or Slack connection.

To format your own approved local sample, use the same JSON structure. `teams` maps anonymous participant IDs to pseudonymous team IDs. Each object in `events` has a unique ID, a `kind` of `request`, `handoff`, or `decision`, and participant IDs in `from` and `to`. Do not submit message text or exact timestamps. Start with the [skill instructions](SKILL.md), including the rules for data access and sharing.
