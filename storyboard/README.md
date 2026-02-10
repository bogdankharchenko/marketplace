# Storyboard Generator

A Claude Code plugin that generates consistent multi-scene storyboard images using Google Gemini.

Each scene maintains visual consistency — same characters, style, and color palette — by using the first scene as a reference for all subsequent images.

## Install

```bash
# Add the marketplace
/plugin marketplace add bogdankharchenko/marketplace

# Install the plugin
/plugin install storyboard@bogdankharchenko-marketplace
```

Or from the terminal:
```bash
claude plugin marketplace add bogdankharchenko/marketplace
claude plugin install storyboard@bogdankharchenko-marketplace
```

## Prerequisites

**Python 3** — the script uses only the standard library, no `pip install` needed.

```bash
python3 --version  # verify it's installed
```

**Gemini API Key** — get one free at https://aistudio.google.com/apikeys, then:

```bash
export GEMINI_API_KEY="your-key-here"
```

To persist it, add the export line to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.).

## Usage

Once installed, use the `/storyboard` command in Claude Code:

```
/storyboard
- A red fox sitting in a snowy forest clearing
- The fox chasing a rabbit through the snow
- The fox resting under a pine tree at sunset
Aspect ratio: 16:9
Resolution: 2K
```

Images are saved to `./storyboard-output/<auto-named-folder>/` in your current directory.

### Options

| Setting | Default | Values |
|---------|---------|--------|
| Aspect ratio | `16:9` | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| Resolution | `2K` | `1K`, `2K`, `4K` |

Just include them in your message naturally:

```
/storyboard
- Scene one description
- Scene two description
Aspect ratio: 9:16
Resolution: 4K
```

### Standalone usage (without Claude Code)

You can also run the Python script directly:

```bash
python3 storyboard.py \
  --scenes '["A fox in snow", "The fox chasing a rabbit"]' \
  --aspect-ratio '16:9' \
  --output-dir './my-storyboard' \
  --resolution '2K'
```

## How it works

1. Generates the first scene image from your description
2. Uses that image as a visual reference for all subsequent scenes
3. Each scene is generated sequentially via the Gemini API to maintain consistency
4. All images are saved as PNGs in the output directory
