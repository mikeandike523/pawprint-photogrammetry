import shutil
import cv2
import numpy as np
from pathlib import Path


def process_folder(folder: Path, output_root: Path, threshold: int = 15):
    """Remove the background from all images in *folder*.

    The threshold is intentionally low so we keep more of the subject and later
    rely on connected components to discard stray pixels.
    """

    image_paths = sorted(
        [p for p in folder.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    )
    if not image_paths:
        print(f"No images found in {folder}")
        return

    images = [cv2.imread(str(p)) for p in image_paths]
    
    # Apply Gaussian blur to all images for better background estimation
    blur_kernel_size = 15  # Adjust this value as needed (must be odd)
    blurred_images = [cv2.GaussianBlur(img, (blur_kernel_size, blur_kernel_size), 0) for img in images]
    
    # compute median background using blurred images
    # median_bg = np.median(np.stack(blurred_images, axis=0), axis=0).astype(np.uint8)
    median_bg = np.mean(np.stack(blurred_images, axis=0), axis=0).astype(np.uint8)


    output_root.mkdir(parents=True, exist_ok=True)

    for path, img, blurred_img in zip(image_paths, images, blurred_images):
        # Use blurred image for difference calculation
        diff = cv2.absdiff(blurred_img, median_bg)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # save an image of this greyscale map next to the final one for debugging
        cv2.imwrite(str(output_root / f"{path.stem}_gray.jpg"), gray)

        mask = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 257, -4
        )

        # save an image of the binary mask next to the final one for debugging
        cv2.imwrite(str(output_root / f"{path.stem}_mask.jpg"), mask)

        kernel = np.ones((5, 5), np.uint8)
        # light cleanup of noise while keeping as much of the subject as possible
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.dilate(mask, kernel, iterations=1)

        # save image of the mask after processing next to the final one for debugging
        cv2.imwrite(str(output_root / f"{path.stem}_processed.jpg"), mask)


        # Filter out small connected components
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        if num_labels > 1:
            # Create a new mask that excludes small components
            filtered_mask = np.zeros_like(mask)
            for label in range(1, num_labels):  # Skip background (label 0)
                area = stats[label, cv2.CC_STAT_AREA]
                if area >= 1000:  # Keep components with 100+ pixels
                    filtered_mask[labels == label] = 255
            mask = filtered_mask

        # Apply mask to the ORIGINAL (non-blurred) image
        fg = cv2.bitwise_and(img, img, mask=mask)
        fg = cv2.cvtColor(fg, cv2.COLOR_BGR2BGRA)
        fg[:, :, 3] = mask
        cv2.imwrite(str(output_root / path.name), fg)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    input_root = repo_root / "background_removal" / "input_files"
    output_root = repo_root / "background_removal" / "output_files"

    shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)

    for folder in sorted(input_root.glob("persp_*")):
        process_folder(folder, output_root / folder.name)


if __name__ == "__main__":
    main()
