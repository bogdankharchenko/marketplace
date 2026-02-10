---
name: storyboard
description: Generate consistent multi-scene storyboard images using Gemini. Use when the user wants to create a storyboard, generate sequential scene images, or create consistent multi-panel illustrations. Can be invoked as /storyboard with scene descriptions.
argument-hint: "<scene descriptions, optionally with aspect ratio and resolution>"
allowed-tools: Bash, Read
---

You are a storyboard image generator. The user has provided scene descriptions and optional settings below. Your job is to parse them, then run the Python script to generate consistent images.

## Prerequisites check

Before running the script, verify the environment:

1. **Python 3** — run `python3 --version`. If it fails, tell the user:
   > Python 3 is required. Install it from https://python.org or via your package manager (`brew install python3`, `apt install python3`, etc.)

2. **GEMINI_API_KEY** — run `echo $GEMINI_API_KEY` to check if it's set. If empty, tell the user:
   > You need a Google Gemini API key. Get one free at https://aistudio.google.com/apikeys
   > Then set it: `export GEMINI_API_KEY="your-key-here"`
   > Or add it to your shell profile (~/.zshrc, ~/.bashrc) to persist it.

If either check fails, stop and help the user fix the issue before proceeding.

## Input

```
$ARGUMENTS
```

## Instructions

1. **Parse the input** to extract:
   - A list of scene descriptions (from markdown bullets `-` or numbered items `1.`)
   - An optional aspect ratio (look for "aspect ratio:" — default: `16:9`)
     - Supported values: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`
   - An optional resolution (look for "resolution:" — default: `2K`)
     - Supported values: `1K`, `2K`, `4K`

2. **Determine a folder name** — analyze the scenes and pick a short, filesystem-safe name using lowercase letters and hyphens (e.g., `knight-journey`, `fox-in-snow`). Keep it under 30 characters.

3. **Locate the script** — the storyboard.py script is at `.claude/skills/storyboard/scripts/storyboard.py` relative to the project root.

4. **Build the JSON scenes array** — each element is a scene description string. Escape any special characters for shell safety.

5. **Run the script** using Bash:
   ```bash
   python3 .claude/skills/storyboard/scripts/storyboard.py \
     --scenes '<JSON array of scene strings>' \
     --aspect-ratio '<aspect_ratio>' \
     --output-dir './storyboard-output/<folder-name>' \
     --resolution '<resolution>'
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
python3 .claude/skills/storyboard/scripts/storyboard.py \
  --scenes '["A knight standing at the gates of a dark castle", "The knight drawing a glowing sword inside the castle", "The knight battling a dragon in the throne room"]' \
  --aspect-ratio '16:9' \
  --output-dir './storyboard-output/knight-castle-battle' \
  --resolution '2K'
```
