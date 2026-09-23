# KPI report

## Trigger

I use this skill to turn discovery notes into a measurement plan. A key performance indicator, or KPI, is a measure used to track progress toward a goal.

A discovery transcript needs to inform what a system should measure.

## Inputs

- The transcript and the project context.
- The stated goals, existing tools, and available baseline numbers.

## What happens

1. Identify the business goals and problems described in the transcript.
2. Extract the measures the speaker explicitly requested.
3. Propose additional measures with a reason and a confidence level.
4. Identify the source, review frequency, and baseline for each measure.
5. Record missing definitions, ownership questions, and implications for the build.

## Outputs

An internal planning document with stated measures, recommendations, open questions, reporting ownership, and notes for system design.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use kpi-report on this fictional equipment-rental discovery transcript. Separate requested metrics from recommendations. Do not invent baseline numbers.
```

## Setup and limits

The report does not calculate live performance. Missing baselines stay unestablished. The standalone skill produces an internal document; review it before adapting it for an external audience. Supply a local output path when you want a saved file.
