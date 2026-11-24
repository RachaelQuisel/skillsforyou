---
name: explain-code
version: 1.1.1
description: Explain how code works by teaching the mental model first, then the mechanism, then one specific gotcha. Use this skill whenever the user says "how does this work", "explain this", "walk me through", "teach me", "what is this doing", "I don't get it", "I'm new to this codebase", or when they paste code and ask about it in any form. Also use when onboarding to an unfamiliar library, function, or system, even if they don't explicitly ask for an explanation. The goal is a reader who could reproduce the code's behavior from memory and predict where it breaks, not just read its signature back.
tags:
  - skill
---

# Explain Code

## What this skill is for

A good code explanation changes what the reader can do next. Before: they can run it. After: they can modify it, debug it, and predict its edge cases.

This skill fights the explanation that reads code out loud as English. "This function takes a list and returns the sum" is not an explanation. It's a signature with extra words.

## The move at the center of every good explanation

Start with the question the reader actually has, not the top of the file.

Readers come in with specific confusion: "why does this not do what I expected?", "what is this one line doing?", "why is there a try/except around nothing?". A great explanation names that confusion in the first sentence and then resolves it. Only after the confusion is resolved do you widen out to the full picture.

Julia Evans does this constantly. Her zines open with a question ("why is my disk full?", "what are tcp states?") and build the answer; she never starts with "here is a definition of X." Dan Abramov's "Just JavaScript" opens each chapter with a "guess the output" quiz because the surprise IS the hook into the mental model.

## The four parts, and what each one is actually doing

### 1. Mental model (what the runtime sees)

Teach the reader how to think about the thing, not what it looks like on the page. A mental model is a small set of rules that lets the reader predict behavior without re-reading the code.

Good mental models are:
- **Concrete.** "Every variable is a wire pointing at a value. Values live in a soup on the side." (Dan Abramov, "Just JavaScript")
- **Falsifiable.** The reader can test them. "If this model is right, then X should happen; if X doesn't happen, the model is wrong."
- **Minimal.** Three rules the reader can hold in their head, not thirty.

Pick an analogy from physical life (mail sorting, a restaurant kitchen, a thermostat, a conveyor belt, a queue at a counter). Never use another piece of code as the analogy; "it's like a stream" is jargon, not a model.

Push one analogy hard rather than sprinkling five shallow ones. If the analogy breaks at some point, say so out loud: "the elevator analogy stops working here because elevators don't have a timeout; what actually happens is...".

### 2. Diagram (what the shape is)

ASCII or a short drawing that shows flow, structure, or timing. The diagram earns its place by making something visible that prose hides: timing between events, which pieces call which, where data moves.

Rules:
- Readable in two seconds. If it isn't, cut it.
- Label the pieces with the names from the code so the reader can map back.
- Show the interesting state, not every state. One timeline, not seven.

If a diagram would be busier than the code, skip it; prose is fine.

### 3. Walkthrough (what happens when it runs)

Trace one concrete call from start to finish with real values. Not `foo(bar)`, use `debounce(fn, 300)` and show the actual millisecond timings. Real values beat variable names every time.

The walkthrough ties each step back to a specific line or function. "At line 7, we clear the existing timer. At line 8, we set a new one. The old callback is now unreachable; garbage collector will clean it up next cycle."

Include the state transitions. What was true before this line? What's true after?

### 4. Gotcha (what trips people up)

One specific mistake, not a general warning. "Watch out for async behavior" is useless. "The first call fires after a 300ms delay, not immediately; if you want fire-immediately-then-wait, that's throttle, not debounce" is a gotcha.

A good gotcha has three properties:
- **Observable.** The reader can see the wrong behavior if they hit it.
- **Specific to this code.** Not a generic programming warning.
- **Named cause.** The gotcha points at the line or design decision that causes the surprise.

If you can't come up with a gotcha, the code either has none worth mentioning (unusual) or you don't understand it well enough yet (more common). Read it again.

## The closer: "now you can read the rest"

End the explanation by pointing at what the reader can now do on their own. "Now you can read the rest of the file; the other three functions are variations on this pattern" or "with this model, you can predict what happens if you call it twice in the same tick: the first call's timer gets dropped on the floor."

This is the Fabien Sanglard move: his "Game Engine Black Books" always end a chapter by saying what the next chapter will build on. The reader leaves equipped, not just informed.

## When to use what

Different asks need different shapes. Pick the shape before writing:

| User says | What they need |
|---|---|
| "How does this work?" (pastes a function) | All four parts, short |
| "I don't get line 12" | Mental model + walkthrough of that line only |
| "Teach me this codebase" | Map first (file-level diagram), then four-parts on the central function |
| "Why does this do X?" | Historical/design context + gotcha; skip the walkthrough |
| "What's the difference between X and Y?" | Side-by-side mental models, one gotcha each |
| "Walk me through this bug" | Walkthrough with real failing values, then the fix |

## Techniques pulled from writers who do this well

- **Julia Evans:** open with the reader's question; use one concrete scenario throughout; show the surprising thing up front.
- **Dan Abramov:** teach a mental model with rules the reader can test; use "guess what this prints" to surface wrong models; show what the runtime sees, not what the syntax looks like.
- **Fabien Sanglard:** start from the constraints (hardware, performance budget, time period); annotate the actual source; name why the author made each choice.
- **Jessica Kerr:** name the human who wrote it and why; explain the connections between parts, not just the parts; respect that "obvious" refactors often break things for reasons the current code encodes.
- **Hillel Wayne:** name the invariants the code maintains; be careful with "always" and "never"; a counterexample beats a definition.
- **LWN kernel walkthroughs:** patch-level ("this line was added because..."); name data structures as characters with roles; timeline of how the subsystem evolved.
- **"Build your own X" tutorials:** start from empty, add one piece at a time; every intermediate state runs; call out what's missing at each step so the reader isn't surprised later.

## Worked examples

See `references/worked-examples.md` for three full-length explanations following the pattern: a debounce function, a React useEffect cleanup, and an Airtable formula. Read it when you want to see the shape at full size.

## Anti-patterns (what makes an explanation bad)

See `references/anti-patterns.md` for the long list. Short version:

- Reading the signature out loud as prose.
- Analogies to other code ("it's like a stream", "like a Promise").
- Walkthroughs that restate each line in English without adding meaning.
- Generic gotchas ("be careful with mutation!").
- Starting at line 1 when line 1 isn't the interesting part.
- Explaining easy parts in detail and waving at the hard parts.
- "This is called a monad" (naming a pattern instead of explaining what it does).
- Seven analogies, each half a sentence long.

## How to know you're done

The reader should be able to:
1. Predict the output of a call you didn't show them.
2. Point to the line that would cause a specific bug you describe.
3. Modify the code to change one behavior without breaking another.

If you can't be confident the reader could do those three things after reading your explanation, it isn't finished. Add the piece that would let them.

## Voice

Conversational. Short sentences for the hard parts; longer ones when the reader can coast. Say "you" to the reader; say "the code" or name the function, not "we." Skip hedging like "basically" and "essentially"; if a thing is approximate, say what's missing.

No em dashes. Use commas, semicolons, parentheses, or two sentences instead.
