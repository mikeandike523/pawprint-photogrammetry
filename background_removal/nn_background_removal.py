import shutil
from pathlib import Path

from rembg import remove
from PIL import Image


def process_folder(folder: Path, output_root: Path) -> None:
    """Remove background from all images in *folder* using a neural network."""
    image_paths = [
        p for p in folder.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    ]
    if not image_paths:
        print(f"No images found in {folder}")
        return

    output_root.mkdir(parents=True, exist_ok=True)

    for path in sorted(image_paths):
        with Image.open(path) as img:
            img = img.convert("RGBA")
            result = remove(img)
            result.save(output_root / path.name)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    input_root = repo_root / "background_removal" / "input_files"
    output_root = repo_root / "background_removal" / "output_files_nn"

    shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)

    for folder in sorted(input_root.glob("persp_*")):
        process_folder(folder, output_root / folder.name)


if __name__ == "__main__":
    main()
