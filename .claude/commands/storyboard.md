---
description: Generate consistent multi-scene storyboard images using Gemini
argument-hint: "<scene descriptions, optionally with aspect ratio>"
allowed-tools:
  - Bash
  - Read
---

You are a storyboard image generator. The user has provided scene descriptions and optional settings below. Your job is to parse them, then run the Python script to generate consistent images.

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

3. **Build the JSON scenes array** — each element is a scene description string. Escape any special characters for shell safety.

4. **Run the script** using Bash:
   ```bash
   python3 /Users/bogdan/Development/generate-images/storyboard.py \
     --scenes '<JSON array of scene strings>' \
     --aspect-ratio '<aspect_ratio>' \
     --output-dir '/Users/bogdan/Development/generate-images/output/<folder-name>' \
     --resolution '<resolution>'
   ```

5. **Report results**:
   - List each generated file path
   - Note any failures or warnings from the script output
   - If all scenes succeeded, confirm the storyboard is complete

## Example

If the user writes:
```
- A knight standing at the gates of a dark castle
- The knight drawing a glowing sword inside the castle
- The knight battling a dragon in the throne room
Aspect ratio: 16:9
```

You would run:
```bash
python3 /Users/bogdan/Development/generate-images/storyboard.py \
  --scenes '["A knight standing at the gates of a dark castle", "The knight drawing a glowing sword inside the castle", "The knight battling a dragon in the throne room"]' \
  --aspect-ratio '16:9' \
  --output-dir '/Users/bogdan/Development/generate-images/output/knight-castle-battle' \
  --resolution '2K'
```
