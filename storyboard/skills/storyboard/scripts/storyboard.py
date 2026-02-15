#!/usr/bin/env python3
"""
Storyboard generator using Replicate's qwen-image model.

Generates consistent multi-scene images by using scene 1's output
(or a user-provided start image) as a reference for all subsequent scenes.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_BASE = "https://api.replicate.com/v1"
MODEL = "qwen/qwen-image"

VALID_ASPECT_RATIOS = [
    "1:1", "2:3", "3:2", "3:4", "4:3",
    "4:5", "5:4", "9:16", "16:9", "21:9",
]

REQUEST_TIMEOUT = 300
POLL_INTERVAL = 3


def load_api_token():
    """Load REPLICATE_API_TOKEN from environment variable or .env file."""
    token = os.environ.get("REPLICATE_API_TOKEN")
    if token:
        return token

    # Check .env in current working directory, then next to this script
    for env_dir in [os.getcwd(), SCRIPT_DIR]:
        env_path = os.path.join(env_dir, ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue
                    if line.startswith("REPLICATE_API_TOKEN="):
                        val = line[len("REPLICATE_API_TOKEN="):].strip().strip("'\"")
                        if val and val != "your_api_token_here":
                            return val

    print("Error: REPLICATE_API_TOKEN not set.", file=sys.stderr)
    print("  Set it with: export REPLICATE_API_TOKEN=\"your-token-here\"", file=sys.stderr)
    print("  Get one at: https://replicate.com/account/api-tokens", file=sys.stderr)
    sys.exit(1)


def api_request(url, token, payload=None, method="POST"):
    """Make a request to the Replicate API."""
    headers = {"Authorization": f"Bearer {token}"}
    data = None

    if payload is not None:
        headers["Content-Type"] = "application/json"
        headers["Prefer"] = "wait"
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} error: {body}", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"URL error: {e.reason}", file=sys.stderr)
        raise


def poll_prediction(token, prediction):
    """Poll until prediction completes."""
    pred_id = prediction["id"]
    poll_url = f"{API_BASE}/predictions/{pred_id}"

    while True:
        time.sleep(POLL_INTERVAL)
        result = api_request(poll_url, token, method="GET")
        status = result.get("status")
        if status == "succeeded":
            return result
        elif status in ("failed", "canceled"):
            error = result.get("error", "Unknown error")
            raise RuntimeError(f"Prediction {status}: {error}")
        # starting / processing — keep polling


def generate_scene(token, prompt, aspect_ratio, reference_image=None, strength=0.65):
    """Generate a single scene image via Replicate."""
    url = f"{API_BASE}/models/{MODEL}/predictions"

    input_data = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "num_inference_steps": 35,
        "guidance": 3.0,
        "output_format": "png",
        "go_fast": True,
    }

    if reference_image:
        input_data["image"] = reference_image
        input_data["strength"] = strength

    result = api_request(url, token, {"input": input_data})

    # If already completed (sync response), return directly
    if result.get("status") == "succeeded":
        return result

    if result.get("status") in ("failed", "canceled"):
        error = result.get("error", "Unknown error")
        raise RuntimeError(f"Prediction {result['status']}: {error}")

    # Otherwise poll until done
    return poll_prediction(token, result)


def download_image(url, filepath):
    """Download image from URL to local file."""
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    with open(filepath, "wb") as f:
        f.write(data)
    print(f"  Saved: {filepath} ({len(data) / 1024:.0f} KB)")


def image_to_data_uri(filepath):
    """Convert a local image file to a data URI for Replicate input."""
    ext = os.path.splitext(filepath)[1].lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime = mime_map.get(ext, "image/png")
    with open(filepath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def main():
    parser = argparse.ArgumentParser(description="Generate storyboard images with Replicate")
    parser.add_argument("--scenes", required=True, help="JSON array of scene descriptions")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--output-dir", required=True, help="Output directory for images")
    parser.add_argument("--start-image", default=None,
                        help="Path or URL to a reference image for character/style consistency")
    parser.add_argument("--strength", type=float, default=0.65,
                        help="How much to deviate from reference (0-1, default: 0.65)")
    args = parser.parse_args()

    if args.aspect_ratio not in VALID_ASPECT_RATIOS:
        print(f"Error: Invalid aspect ratio '{args.aspect_ratio}'. "
              f"Must be one of: {', '.join(VALID_ASPECT_RATIOS)}", file=sys.stderr)
        sys.exit(1)

    if not 0 <= args.strength <= 1:
        print(f"Error: Strength must be between 0 and 1, got {args.strength}", file=sys.stderr)
        sys.exit(1)

    try:
        scenes = json.loads(args.scenes)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON for --scenes: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(scenes, list) or len(scenes) == 0:
        print("Error: --scenes must be a non-empty JSON array of strings", file=sys.stderr)
        sys.exit(1)

    print(f"Storyboard: {len(scenes)} scene(s), {args.aspect_ratio}")
    print(f"Output: {args.output_dir}")
    if args.start_image:
        print(f"Start image: {args.start_image}")
    print()

    token = load_api_token()
    os.makedirs(args.output_dir, exist_ok=True)

    # Prepare start image reference if provided
    reference_input = None
    if args.start_image:
        if args.start_image.startswith(("http://", "https://", "data:")):
            reference_input = args.start_image
        else:
            if not os.path.exists(args.start_image):
                print(f"Error: Start image not found: {args.start_image}", file=sys.stderr)
                sys.exit(1)
            reference_input = image_to_data_uri(args.start_image)

    scene1_output_url = None
    saved_count = 0

    for i, description in enumerate(scenes, start=1):
        print(f"[{i}/{len(scenes)}] Generating: {description[:80]}...")

        # Determine reference image and prompt for this scene
        ref = None
        if i == 1 and reference_input:
            ref = reference_input
            prompt = (
                "Using the same characters, art style, and color palette "
                "from the reference image. Generate: " + description
            )
        elif i > 1 and scene1_output_url:
            ref = scene1_output_url
            prompt = (
                "Maintain the same characters, art style, and color palette. "
                "Generate a new scene: " + description
            )
        else:
            prompt = description

        try:
            result = generate_scene(token, prompt, args.aspect_ratio, ref, args.strength)
            output = result.get("output")

            if not output:
                print(f"  Warning: No image returned for scene {i}", file=sys.stderr)
                continue

            img_url = output[0] if isinstance(output, list) else output
            filepath = os.path.join(args.output_dir, f"scene-{i}.png")
            download_image(img_url, filepath)
            saved_count += 1

            # Store scene 1's output URL as reference for subsequent scenes
            if i == 1:
                scene1_output_url = img_url

        except Exception as e:
            print(f"  Error generating scene {i}: {e}", file=sys.stderr)
        print()

    print(f"Generated {saved_count}/{len(scenes)} images in {args.output_dir}")


if __name__ == "__main__":
    main()
