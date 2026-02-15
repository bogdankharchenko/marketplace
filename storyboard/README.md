# Storyboard Generator

A Claude Code plugin that generates consistent multi-scene storyboard images using Replicate's SeedDream 4 model by ByteDance.

Each scene maintains visual consistency — same characters, style, and color palette — by using the first scene as a reference for all subsequent images. You can also provide your own start image (e.g., a character design) to maintain consistency from the beginning.

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

**Replicate API Token** — get one at https://replicate.com/account/api-tokens, then:

```bash
export REPLICATE_API_TOKEN="your-token-here"
```

To persist it, add the export line to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.).

The skill will also prompt you for the token on first use and save it to `.env` automatically.

## Usage

Once installed, use the `/storyboard` command in Claude Code:

```
/storyboard
- A red fox sitting in a snowy forest clearing
- The fox chasing a rabbit through the snow
- The fox resting under a pine tree at sunset
Aspect ratio: 16:9
```

Images are saved to `./storyboard-output/<auto-named-folder>/` in your current directory.

### Start image

The skill will ask if you have a reference image for character or style consistency. This is useful when you want to maintain a specific character design or art style across all scenes. You can provide a local file path or URL.

### Options

| Setting | Default | Values |
|---------|---------|--------|
| Aspect ratio | `16:9` | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `9:16`, `16:9`, `21:9` |
| Size | `2K` | `1K` (1024px), `2K` (2048px), `4K` (4096px) |

Just include them in your message naturally:

```
/storyboard
- Scene one description
- Scene two description
Aspect ratio: 9:16
Size: 4K
```

### Standalone usage (without Claude Code)

You can also run the Python script directly:

```bash
python3 storyboard.py \
  --scenes '["A fox in snow", "The fox chasing a rabbit"]' \
  --aspect-ratio '16:9' \
  --size '2K' \
  --output-dir './my-storyboard'

# With a reference image:
python3 storyboard.py \
  --scenes '["A fox in snow", "The fox chasing a rabbit"]' \
  --aspect-ratio '16:9' \
  --size '2K' \
  --output-dir './my-storyboard' \
  --start-image './my-character.png'
```

## How it works

1. Asks if you have a reference/start image for consistency
2. Generates the first scene image from your description (using the start image if provided)
3. Uses that image as a visual reference for all subsequent scenes via the `image_input` parameter
4. Each scene is generated sequentially via the Replicate API to maintain consistency
5. All images are saved as PNGs in the output directory
