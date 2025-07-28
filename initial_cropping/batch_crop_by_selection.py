import shutil
import cv2
from pathlib import Path


def select_roi(sample_image_path: Path):
    """Display image and let user select ROI rectangle.

    Returns (x, y, w, h) or raises ValueError if selection was cancelled.
    """
    img = cv2.imread(str(sample_image_path))
    if img is None:
        raise ValueError(f"Failed to load sample image: {sample_image_path}")

    # Downsample the image by a factor of 4 solely for ROI selection.  This
    # speeds up rendering of large images and makes it easier to select a
    # region on high‑resolution photos.  The returned rectangle will later be
    # scaled back up to match the original resolution.
    scale = 4
    display_img = cv2.resize(
        img,
        (img.shape[1] // scale, img.shape[0] // scale),
        interpolation=cv2.INTER_AREA,
    )

    roi_down = cv2.selectROI(
        "Select ROI and press ENTER",
        display_img,
        fromCenter=False,
        showCrosshair=True,
    )
    cv2.destroyAllWindows()

    x, y, w, h = roi_down
    if w == 0 or h == 0:
        raise ValueError("ROI selection cancelled or invalid")

    # Scale the selection back up to the original image size and clamp it to
    # the image bounds in case rounding caused a slight over‑run.
    x = int(x * scale)
    y = int(y * scale)
    w = int(w * scale)
    h = int(h * scale)
    w = min(w, img.shape[1] - x)
    h = min(h, img.shape[0] - y)

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

    shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)

    folders = sorted([p for p in input_root.glob("persp_*") if p.is_dir()])
    if not folders:
        print(f"No perspective folders found in {input_root}")
        return

    for folder in folders:
        image_paths = [p for p in folder.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        if not image_paths:
            print(f"No images found in {folder} for ROI selection")
            continue

        print(f"\nSelecting ROI for {folder.name}...")
        try:
            crop_rect = select_roi(image_paths[0])
        except ValueError as e:
            print(e)
            print(f"Skipping folder {folder.name}")
            continue

        crop_folder(folder, output_root / folder.name, crop_rect)


if __name__ == "__main__":
    main()
