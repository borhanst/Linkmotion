# Onboarding

First-interaction greeting. When the user's first message is vague, exploratory,
or asks what you can do, run this before anything else.

## Goal

Get the user from "curious" to "making a video" in under 60 seconds.

## Step 1 - Run preflight

```bash
python -m tools.tool_registry
```

Present the capability menu in plain language. Don't dump the raw registry.

## Step 2 - Classify the setup

Ask (at most one question): what kind of video do they want?

- AI news story (single event)
- LLM / model release announcement
- Long-form deep-dive / roundup
- Repo walkthrough / screen demo

## Step 3 - Offer starter prompts

Tailor to their available tools. Zero-key path is the default:

- "Make a 60-second Short about the new GPT-5 release"
- "Make a 7-minute deep-dive on how Claude Code works under the hood"
- "Make a model-release explainer for the new Gemini Omni Flash"

## Step 4 - Pick the pipeline

Map the request to a manifest in `pipeline_defs/` and go to Rule Zero.

## Skip onboarding

When the user arrives with a specific, actionable request (e.g. "Make a
60-second Short about the new GPT-5 release"), skip onboarding and go
straight to Rule Zero.