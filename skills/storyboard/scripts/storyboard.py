#!/usr/bin/env python3
"""
Storyboard generator using Google Gemini's image generation.

Generates consistent multi-scene images by using scene 1's output
as a reference image for all subsequent scenes (sequential API calls).
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "gemini-3-pro-image-preview"

VALID_ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
VALID_RESOLUTIONS = ["1K", "2K", "4K"]

REQUEST_TIMEOUT = 180


def load_api_key():
    """Load GEMINI_API_KEY from environment variable or .env file."""
    # Check environment variable first (works everywhere)
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    # Fall back to .env file next to this script
    env_path = os.path.join(SCRIPT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if line.startswith("GEMINI_API_KEY="):
                    key = line[len("GEMINI_API_KEY="):].strip().strip("'\"")
                    if key and key != "your_api_key_here":
                        return key

    print("Error: GEMINI_API_KEY not set.", file=sys.stderr)
    print("  Set it with: export GEMINI_API_KEY=\"your-key-here\"", file=sys.stderr)
    print("  Get a free key at: https://aistudio.google.com/apikeys", file=sys.stderr)
    sys.exit(1)


def gemini_request(url, api_key, payload, timeout=REQUEST_TIMEOUT):
    """POST to Gemini API with error handling."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} error: {body}", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"URL error: {e.reason}", file=sys.stderr)
        raise


def extract_image_and_text(result):
    """Extract base64 image data and text from a generateContent response."""
    image_data = None
    response_text = ""
    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                image_data = part["inlineData"]["data"]
            elif "text" in part:
                response_text = part["text"]
    return image_data, response_text


def generate_scene(description, aspect_ratio, resolution, api_key, reference_base64=None):
    """Generate a scene image. If reference_base64 is provided, include it as reference."""
    url = f"{BASE_URL}/models/{MODEL}:generateContent"

    parts = []
    if reference_base64:
        parts.append({
            "inlineData": {
                "mimeType": "image/png",
                "data": reference_base64,
            }
        })
        parts.append({
            "text": (
                "Using the same characters, style, and color palette "
                "shown in the reference image, generate: " + description
            ),
        })
    else:
        parts.append({"text": description})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": resolution,
            },
        },
    }

    result = gemini_request(url, api_key, payload)
    return extract_image_and_text(result)


def save_image(base64_data, filepath):
    """Decode base64 and write PNG file."""
    img_bytes = base64.b64decode(base64_data)
    with open(filepath, "wb") as f:
        f.write(img_bytes)
    print(f"  Saved: {filepath} ({len(img_bytes) / 1024:.0f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Generate storyboard images with Gemini")
    parser.add_argument("--scenes", required=True, help="JSON array of scene descriptions")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--output-dir", required=True, help="Output directory for images")
    parser.add_argument("--resolution", default="2K", help="Image resolution: 1K, 2K, 4K (default: 2K)")
    args = parser.parse_args()

    if args.aspect_ratio not in VALID_ASPECT_RATIOS:
        print(f"Error: Invalid aspect ratio '{args.aspect_ratio}'. Must be one of: {', '.join(VALID_ASPECT_RATIOS)}", file=sys.stderr)
        sys.exit(1)

    if args.resolution not in VALID_RESOLUTIONS:
        print(f"Error: Invalid resolution '{args.resolution}'. Must be one of: {', '.join(VALID_RESOLUTIONS)}", file=sys.stderr)
        sys.exit(1)

    try:
        scenes = json.loads(args.scenes)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON for --scenes: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(scenes, list) or len(scenes) == 0:
        print("Error: --scenes must be a non-empty JSON array of strings", file=sys.stderr)
        sys.exit(1)

    print(f"Storyboard: {len(scenes)} scene(s), {args.aspect_ratio}, {args.resolution}")
    print(f"Output: {args.output_dir}")
    print()

    api_key = load_api_key()
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate scene 1 (no reference image)
    print(f"[1/{len(scenes)}] Generating: {scenes[0][:80]}...")
    scene1_base64, scene1_text = generate_scene(scenes[0], args.aspect_ratio, args.resolution, api_key)

    if not scene1_base64:
        print("Error: No image returned for scene 1", file=sys.stderr)
        sys.exit(1)

    save_image(scene1_base64, os.path.join(args.output_dir, "scene-1.png"))
    if scene1_text:
        print(f"  Text: {scene1_text[:200]}")
    print()

    # Generate remaining scenes sequentially, each referencing scene 1
    saved_count = 1
    for i, description in enumerate(scenes[1:], start=2):
        print(f"[{i}/{len(scenes)}] Generating: {description[:80]}...")
        try:
            img_base64, text = generate_scene(
                description, args.aspect_ratio, args.resolution, api_key,
                reference_base64=scene1_base64,
            )
            if img_base64:
                save_image(img_base64, os.path.join(args.output_dir, f"scene-{i}.png"))
                saved_count += 1
                if text:
                    print(f"  Text: {text[:200]}")
            else:
                print(f"  Warning: No image returned for scene {i}", file=sys.stderr)
        except Exception as e:
            print(f"  Error generating scene {i}: {e}", file=sys.stderr)
        print()

    print(f"Generated {saved_count}/{len(scenes)} images in {args.output_dir}")


if __name__ == "__main__":
    main()
