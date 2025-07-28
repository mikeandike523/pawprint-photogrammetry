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
