#!/usr/bin/env python3
"""Validate the portable parts of a Codex v2 pet package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


EXPECTED_SIZE = (1536, 2288)


def validate_pet(pet_dir: Path) -> dict[str, object]:
    manifest_path = pet_dir / "pet.json"
    if not manifest_path.is_file():
        raise ValueError(f"missing manifest: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required = ("id", "displayName", "description", "spriteVersionNumber", "spritesheetPath")
    missing = [key for key in required if key not in manifest]
    if missing:
        raise ValueError(f"pet.json is missing: {', '.join(missing)}")
    if manifest["spriteVersionNumber"] != 2:
        raise ValueError("spriteVersionNumber must be 2")

    sprite_path = pet_dir / str(manifest["spritesheetPath"])
    if not sprite_path.is_file():
        raise ValueError(f"missing spritesheet: {sprite_path}")
    with Image.open(sprite_path) as image:
        if image.size != EXPECTED_SIZE:
            raise ValueError(
                f"spritesheet must be 1536x2288; found {image.width}x{image.height}"
            )
        image.verify()
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pet_dir", type=Path)
    args = parser.parse_args()

    try:
        manifest = validate_pet(args.pet_dir.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"{manifest['id']} is a valid Codex v2 pet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
