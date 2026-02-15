---
name: storyboard
description: Generate consistent multi-scene storyboard images using Replicate. Use when the user wants to create a storyboard, generate sequential scene images, or create consistent multi-panel illustrations. Can be invoked as /storyboard with scene descriptions.
argument-hint: "<scene descriptions, optionally with aspect ratio and strength>"
allowed-tools: Bash, Read
---

You are a storyboard image generator. The user has provided scene descriptions and optional settings below. Your job is to parse them, then run the Python script to generate consistent images.

## Prerequisites check

Before running the script, verify the environment:

1. **Python 3** — run `python3 --version`. If it fails, tell the user:
   > Python 3 is required. Install it from https://python.org or via your package manager (`brew install python3`, `apt install python3`, etc.)

2. **REPLICATE_API_TOKEN** — run `echo $REPLICATE_API_TOKEN` to check if it's set. If empty, check for a `.env` file in the current directory:
   ```bash
   grep REPLICATE_API_TOKEN .env 2>/dev/null
   ```
   If neither is set, tell the user:
   > You need a Replicate API token. Get one at https://replicate.com/account/api-tokens
   > Please paste your token and I'll save it to `.env` for future use.

   When the user provides their token, **save it to `.env`** in the current working directory:
   - If `.env` exists, append `REPLICATE_API_TOKEN=<token>` to it
   - If `.env` does not exist, create it with `REPLICATE_API_TOKEN=<token>`

   Then stop and wait for the user to provide the token before continuing.

If Python 3 is missing, stop and help the user fix the issue before proceeding.

## Start image prompt

After prerequisites pass, **ask the user** if they have a reference image for character or style consistency:

> Do you have a reference image you'd like to use for consistency across scenes? For example, a character design, style reference, or existing illustration. If so, provide the file path or URL. Otherwise, I'll generate everything from scratch.

Wait for the user's response before proceeding. If they provide a path or URL, use it with `--start-image`. If they decline, proceed without it.

## Input

```
$ARGUMENTS
```

## Instructions

1. **Parse the input** to extract:
   - A list of scene descriptions (from markdown bullets `-` or numbered items `1.`)
   - An optional aspect ratio (look for "aspect ratio:" — default: `16:9`)
     - Supported values: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`
   - An optional strength (look for "strength:" — default: `0.65`)
     - Range: `0.0` to `1.0` — lower values keep scenes closer to the reference image, higher values allow more creative deviation

2. **Determine a folder name** — analyze the scenes and pick a short, filesystem-safe name using lowercase letters and hyphens (e.g., `knight-journey`, `fox-in-snow`). Keep it under 30 characters.

3. **Locate the script** — find `storyboard.py` bundled with this plugin:
   ```bash
   SCRIPT="$(find . ~/.claude "$HOME/Library/Application Support/Claude" -path '*/skills/storyboard/scripts/storyboard.py' -print -quit 2>/dev/null)"
   ```

4. **Build the JSON scenes array** — each element is a scene description string. Escape any special characters for shell safety.

5. **Run the script** using Bash:
   ```bash
   SCRIPT="$(find . ~/.claude "$HOME/Library/Application Support/Claude" -path '*/skills/storyboard/scripts/storyboard.py' -print -quit 2>/dev/null)"
   python3 "$SCRIPT" \
     --scenes '<JSON array of scene strings>' \
     --aspect-ratio '<aspect_ratio>' \
     --output-dir './storyboard-output/<folder-name>' \
     [--start-image '<path-or-url>'] \
     [--strength '<strength>']
   ```

   Note: output goes to `./storyboard-output/<folder-name>` in the user's **current working directory**.

6. **Report results**:
   - List each generated file path
   - Note any failures or warnings from the script output
   - If all scenes succeeded, confirm the storyboard is complete

## Example

If the user writes:
```
/storyboard
- A knight standing at the gates of a dark castle
- The knight drawing a glowing sword inside the castle
- The knight battling a dragon in the throne room
Aspect ratio: 16:9
```

You would run:
```bash
SCRIPT="$(find . ~/.claude "$HOME/Library/Application Support/Claude" -path '*/skills/storyboard/scripts/storyboard.py' -print -quit 2>/dev/null)"
python3 "$SCRIPT" \
  --scenes '["A knight standing at the gates of a dark castle", "The knight drawing a glowing sword inside the castle", "The knight battling a dragon in the throne room"]' \
  --aspect-ratio '16:9' \
  --output-dir './storyboard-output/knight-castle-battle'
```

With a start image:
```bash
python3 "$SCRIPT" \
  --scenes '["The knight entering a dark forest", "The knight finding a hidden temple"]' \
  --aspect-ratio '16:9' \
  --output-dir './storyboard-output/knight-forest' \
  --start-image './my-character.png' \
  --strength '0.65'
```
