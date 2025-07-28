import cv2
import numpy as np
from pathlib import Path


def process_folder(folder: Path, output_root: Path, threshold: int = 15):
    """Remove the background from all images in *folder*.

    The threshold is intentionally low so we keep more of the subject and later
    rely on connected components to discard stray pixels.
    """

    image_paths = sorted([p for p in folder.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}])
    if not image_paths:
        print(f"No images found in {folder}")
        return

    images = [cv2.imread(str(p)) for p in image_paths]
    # compute median background
    median_bg = np.median(np.stack(images, axis=0), axis=0).astype(np.uint8)

    output_root.mkdir(parents=True, exist_ok=True)

    for path, img in zip(image_paths, images):
        diff = cv2.absdiff(img, median_bg)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5, 5), np.uint8)
        # light cleanup of noise while keeping as much of the subject as possible
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.dilate(mask, kernel, iterations=1)

        # keep only the largest connected component
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        if num_labels > 1:
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            mask = np.where(labels == largest_label, 255, 0).astype(np.uint8)

        fg = cv2.bitwise_and(img, img, mask=mask)
        fg = cv2.cvtColor(fg, cv2.COLOR_BGR2BGRA)
        fg[:, :, 3] = mask
        cv2.imwrite(str(output_root / path.name), fg)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    input_root = repo_root / 'background_removal' / 'input_files'
    output_root = repo_root / 'background_removal' / 'output_files'

    for folder in sorted(input_root.glob('persp_*')):
        process_folder(folder, output_root / folder.name)


if __name__ == '__main__':
    main()
