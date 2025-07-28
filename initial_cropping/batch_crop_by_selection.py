import cv2
from pathlib import Path


def select_roi(sample_image_path: Path):
    """Display image and let user select ROI rectangle.

    Returns (x, y, w, h) or raises ValueError if selection was cancelled.
    """
    img = cv2.imread(str(sample_image_path))
    if img is None:
        raise ValueError(f"Failed to load sample image: {sample_image_path}")

    roi = cv2.selectROI(
        "Select ROI and press ENTER",
        img,
        fromCenter=False,
        showCrosshair=True,
    )
    cv2.destroyAllWindows()
    x, y, w, h = roi
    if w == 0 or h == 0:
        raise ValueError("ROI selection cancelled or invalid")
    return x, y, w, h


def crop_folder(folder: Path, output_root: Path, crop_rect):
    """Crop all images in *folder* using *crop_rect* and write to output."""
    x, y, w, h = crop_rect
    output_root.mkdir(parents=True, exist_ok=True)

    image_paths = [p for p in folder.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    for path in sorted(image_paths):
        img = cv2.imread(str(path))
        if img is None:
            print(f"Skipping unreadable image {path}")
            continue
        cropped = img[y : y + h, x : x + w]
        cv2.imwrite(str(output_root / path.name), cropped)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    input_root = repo_root / "initial_cropping" / "input_files"
    output_root = repo_root / "initial_cropping" / "output_files"
    output_root.mkdir(parents=True, exist_ok=True)

    folders = sorted([p for p in input_root.glob("persp_*") if p.is_dir()])
    if not folders:
        print(f"No perspective folders found in {input_root}")
        return

    # Use first image of first folder as sample for ROI selection
    first_folder = folders[0]
    sample_images = [p for p in first_folder.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    if not sample_images:
        print(f"No images found in {first_folder} for ROI selection")
        return

    try:
        crop_rect = select_roi(sample_images[0])
    except ValueError as e:
        print(e)
        return

    for folder in folders:
        crop_folder(folder, output_root / folder.name, crop_rect)


if __name__ == "__main__":
    main()
