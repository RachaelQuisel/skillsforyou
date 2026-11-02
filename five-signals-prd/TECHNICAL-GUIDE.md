# Five-signals PRD

## Trigger

I use this format to explain a proposed system and the decisions behind it. A product requirements document, or PRD, should make the goal, assumptions, and limits clear enough to review.

Use this skill when a proposal needs a design decision, a requirements document, or a structured technical walkthrough.

## Inputs

- The outcome people need from the system.
- What is outside the scope.
- Relevant quantities, such as volume, traffic, storage, and response-time requirements.
- Known constraints and assumptions.
- The intended audience.

## What happens

1. The assistant identifies whether the document is for a client, an internal review, or an interview exercise.
2. It asks for missing requirements that could change the design.
3. It frames the problem and calculates the estimates that matter to the decision.
4. It proposes a design and explains why it fits.
5. It compares the alternatives and recommends one option.
6. It pairs failure cases with specific responses.
7. When growth requirements are available, it describes what would trigger a design change.
8. It checks for missing assumptions, capacity estimates, scope limits, and consequences of failure.

## Outputs

A Markdown document with:

- The intended outcome.
- A frame-and-estimate block covering inputs, scope, storage, operations, response time, and the resulting decision.
- Explicit assumptions.
- A design explanation and diagram.
- A comparison of alternatives with one recommendation.
- Failure cases and mitigations.
- An optional path for future growth.

## Try it

Load `SKILL.md` in your assistant:

```text
Use five-signals-prd for a fictional equipment reservation service.
It serves 200 people and accepts up to 30 requests per minute.
The booking response should take less than two seconds.
Payments are outside scope.
Ask for any missing assumption that would change the design.
```

## Fictional example

For an equipment reservation service, the comparison might consider a shared table, a low-code application, and a custom service. The recommendation should explain which requirement drives the choice. The failure section should address two people trying to reserve the same item.

## Dependencies and attribution

The frame-and-estimate structure is included in `SKILL.md`. No companion skill or private framework file is required.

See [methodology sources](references/methodology.md) for influences on estimation and design review. Preserve those credits when adapting the format.

## Limits

Estimates are assumptions to examine. They are not measured performance results. This skill produces a design document; it does not build or validate the proposed system.
