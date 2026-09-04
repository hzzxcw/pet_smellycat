#!/usr/bin/env python3
"""Install a validated Codex pet package into the local pets directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from verify_pet import validate_pet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pet_dir", type=Path)
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path.home() / ".codex" / "pets",
        help="parent directory for installed pets",
    )
    parser.add_argument("--force", action="store_true", help="replace an existing package")
    args = parser.parse_args()

    source = args.pet_dir.resolve()
    try:
        manifest = validate_pet(source)
        target = args.destination.expanduser().resolve() / str(manifest["id"])
        if target.exists():
            if not args.force:
                raise ValueError(f"destination already exists: {target}; use --force to replace it")
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"installed {manifest['displayName']} at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
