import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify_pet.py"
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install_pet.py"


def make_pet(root: Path, *, size: tuple[int, int] = (1536, 2288)) -> Path:
    pet_dir = root / "smelly-cat-gao"
    pet_dir.mkdir(parents=True)
    (pet_dir / "pet.json").write_text(
        json.dumps(
            {
                "id": "smelly-cat-gao",
                "displayName": "Smelly Cat Gao",
                "description": "Test fixture",
                "spriteVersionNumber": 2,
                "spritesheetPath": "spritesheet.webp",
            }
        ),
        encoding="utf-8",
    )
    Image.new("RGBA", size, (0, 0, 0, 0)).save(
        pet_dir / "spritesheet.webp", "WEBP", lossless=True
    )
    return pet_dir


class VerifyPetTests(unittest.TestCase):
    def test_accepts_a_valid_v2_pet_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            pet_dir = make_pet(Path(temporary_directory))
            result = subprocess.run(
                [sys.executable, str(VERIFY_SCRIPT), str(pet_dir)],
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid Codex v2 pet", result.stdout)

    def test_rejects_the_wrong_atlas_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            pet_dir = make_pet(Path(temporary_directory), size=(1536, 1872))
            result = subprocess.run(
                [sys.executable, str(VERIFY_SCRIPT), str(pet_dir)],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("1536x2288", result.stderr)


class InstallPetTests(unittest.TestCase):
    def test_installs_package_under_its_manifest_id(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = make_pet(root / "source")
            destination = root / "pets"
            result = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL_SCRIPT),
                    str(source),
                    "--destination",
                    str(destination),
                ],
                capture_output=True,
                text=True,
            )

            installed = destination / "smelly-cat-gao"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads((installed / "pet.json").read_text(encoding="utf-8"))["id"],
                "smelly-cat-gao",
            )
            self.assertTrue((installed / "spritesheet.webp").is_file())


if __name__ == "__main__":
    unittest.main()
