# Post to huddle

## Trigger

I use this skill to deliver an approved update to the correct project Slack channel.

A finished message needs to be shared in a configured project channel.

## Inputs

- The project name and verified destination channel.
- The message to send.
- Approval of the content and destination.

## What happens

1. Resolve the destination using the configured routing.
2. Format the message for Slack.
3. Keep it under 40 lines and shorten large task groups.
4. Remove user mentions and channel-wide tags.
5. Show the final message and destination for confirmation.
6. After approval, post the message through Slack.

## Outputs

A message posted to the selected channel when sending is authorized and the integration succeeds.

## Try it with a fictional example

Once the source skill is installed and configured, use a request like this:

```text
Use post-to-huddle to prepare a fictional weekly inventory update. Show the message and destination for approval before sending.
```

## Setup and limits

This is an external communication workflow. Provide an explicit channel ID or an authorized routing source. The package contains no account or channel mappings. Documentation examples do not demonstrate a successful send, and this README does not grant permission to post.
