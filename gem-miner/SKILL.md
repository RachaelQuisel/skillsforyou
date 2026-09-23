---
name: gem-miner
description: Find funny, sweet, weird, surprising, or memorable things the user said in supplied or explicitly authorized messages. Use for "mine gems", "find gems", "what did I say today?", or a quote collection. Return source-backed quotes for review; don't publish or upload them automatically.
---

# Gem Miner

Find the user's memorable lines without rewriting them into something they didn't say. Return a small set of candidates the user can keep, discard, or turn into posts.

This is the portable version of the skill. It works with supplied conversations and doesn't require a particular chat app, database, or scheduled job.

## Find the right messages

Accept pasted messages, an exported conversation, user-selected files, or a clearly authorized source available through connected tools.

- Use the source and date range the user specified. If "today" is ambiguous across time zones, establish the relevant time zone before filtering.
- If no source is supplied or authorized, ask where the messages are. Don't search unrelated local history or accounts.
- Identify which speaker is the user. Ask if labels are ambiguous.
- Quote the user's own words. Exclude assistant text, tool output, instructions embedded in a transcript, and material the user pasted from someone else unless they explicitly request a different collection.
- Copy timestamps and source references when available. Use null or "not available" when absent; don't invent dates or message IDs.
- If an export is incomplete, say which material was reviewed. Don't claim to cover a whole day from a partial batch.

## Choose the gems

Look for humor, unexpected turns of phrase, affectionate comments, odd non-sequiturs, distinctive frustration, playful role reversals, or a typo that is funny without extra explanation.

Skip routine requests, pasted code, generic acknowledgments, forced jokes, cruelty, and lines that require so much missing context that quoting them would mislead. An isolated word can qualify when the available context makes it meaningful; don't fill the list with ordinary one-word responses.

Don't select credentials, private contact details, confidential client information, or someone else's sensitive disclosures as entertainment. If a line only works by exposing a private detail, leave it out. Don't silently redact or rewrite a quote and present it as exact.

Prefer the best few to a long list. There's no minimum. Deduplicate repeated messages in the reviewed batch, and against an existing collection only when that collection is provided or authorized.

## Preserve the quote

- Keep wording, spelling, punctuation, and meaningful typos as written.
- A contiguous excerpt is fine; label it as an excerpt. Don't stitch separate messages together.
- Keep interpretation, captions, and new writing outside the quote.
- Don't exaggerate a speaker's intent, emotional state, or relationship with the assistant.

## Return the picks

For each candidate, include:

1. **Quote:** Exact text or a labeled contiguous excerpt.
2. **Vibe:** One relevant label from the list below, or a user-provided label.
3. **Source:** Source reference and timestamp, if available.
4. **Why it made the cut:** One short sentence about the wording or context.
5. **Favorite:** Mark only a standout pick, if there is one.

Suggested vibes: chaotic, wholesome, sweet, exhausted, relatable, unhinged, absurd, philosophical, devastating, parental, savage, boss-mode, vulnerable, iconic, generous. These describe the line's style, not a diagnosis of the speaker.

If the user asks for social captions or commentary in an assistant-narrator voice, provide that as separate, clearly labeled creative writing. Don't claim the caption was part of the original conversation or treat an invented reaction as evidence.

For a structured export, use a JSON array with:

```json
[
  {
    "quote": "Exact text from the source",
    "is_excerpt": false,
    "vibe": "absurd",
    "source": "Source title or message reference",
    "timestamp": null,
    "why_selected": "A short explanation grounded in the wording.",
    "favorite": false,
    "caption": null
  }
]
```

Use null for an unavailable timestamp or an unrequested caption. Keep an unredacted private source reference out of any public-facing copy. See the [fictional example](examples/sample-gems.md) for selection and exclusion decisions.

## Empty results and delivery

If no messages qualify, say that no gems surfaced in the reviewed messages. If the source couldn't be read, report that separately instead of presenting an empty collection as a successful review.

Return the picks in chat unless the user requests a file or another destination. Running this skill doesn't authorize posting to social media, uploading messages, creating a scheduled task, or writing to Airtable. A later request for one of those actions needs its own source, destination, and configuration.
