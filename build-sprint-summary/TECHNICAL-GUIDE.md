# Build sprint summary

## Trigger

I use this skill to turn grouped task data into a status update that starts with work needing attention.

Task data has already been collected and needs a readable sprint summary.

## Inputs

- The project name and sprint dates.
- Tasks grouped as In Progress, At Risk, Done, Carried, or Cancelled.
- Logged hours for completed tasks, when available.

## What happens

1. Count completed tasks as velocity.
2. Calculate completion rate as Done divided by Done plus In Progress plus Carried.
3. Identify overdue tasks that are still in progress.
4. Sort active work by due date and completed work by completion date.
5. Show active work first, followed by completed work, carried work, and totals.
6. Omit logged hours when the source values are mostly missing.

## Outputs

Formatted summary text that can be reviewed before it is saved or sent.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use build-sprint-summary for a fictional sprint with 6 done, 2 in progress, and 2 carried tasks. Use the supplied task dates to identify overdue work.
```

## Setup and limits

That fictional sprint has a 60% completion rate. At Risk is a subset of active work, not another group to add to the denominator. The skill formats supplied data; it does not fetch tasks or post to Slack. Empty sprint totals need an explicit no-data treatment.
