# Photogrammetry Background Removal

This repository includes a small utility script that removes the common background from sets of images captured on a turntable. Each set should live inside `background_removal/input_files` within a folder named `persp_<index>`, where the folder contains all rotations of that perspective. The script will produce background‐free versions of each image in `background_removal/output_files/persp_<index>`.

## Usage
1. Place your input folders in `background_removal/input_files`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the script:

```bash
python background_removal/batch_background_removal.py
```

The script computes a median background from each folder and removes it from every image, outputting PNG images with an alpha channel containing the transparency mask.

## Initial Cropping Utility
Sometimes the captured images include a large amount of empty space around the turntable.  The
`initial_cropping` folder contains a helper script to manually select a region of interest (ROI)
and crop every image to that rectangle.

1. Place the input perspective folders in `initial_cropping/input_files`.
2. Run the script:

   ```bash
   python initial_cropping/batch_crop_by_selection.py
   ```

3. A window will open showing the first image.  Draw a rectangle around the desired area and
   press <kbd>Enter</kbd>.  All images will be cropped to this selection and written to
   `initial_cropping/output_files`.
