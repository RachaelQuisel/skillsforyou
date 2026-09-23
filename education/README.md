# Education

## Trigger

I use this skill for a detailed automation handoff that an operator, owner, and engineer can each use.

A substantial automation needs a full operating and maintenance document.

## Inputs

- The implementation and current configuration.
- The daily operator’s role.
- Verified run behavior, known errors, design decisions, and open work.

## What happens

1. Review the source and available evidence.
2. Write the operator’s quick read.
3. Explain triggers and the checks that allow or block a run.
4. Describe the data moved and the path through each system.
5. Document how duplicate runs are prevented.
6. Explain errors, design decisions, recovery, and versioning.
7. List engineering file locations and unresolved work.

## Outputs

A document with eleven sections: Quick Read, What this does, Triggers, Gates, Numbering System or Data It Moves, Pipeline, Race Guard, Common Errors, Owners and Architects, Files and Locations, and Open Items.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use education to document a fictional equipment-return workflow from the supplied configuration. Explain missing evidence rather than inventing operating behavior.
```

## Setup and limits

Every section remains present. A section that does not apply needs a short explanation. Choose the operator’s role from the supplied context. No private exemplars or operator mappings are included. For a shorter explanation, use auto or how-it-works-doc.
