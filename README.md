# Model Inference for Thermal Image Analysis

This project provides inference capabilities for thermal image analysis using PatchCore anomaly detection. It can detect various types of electrical faults including point overloads, wire overloads, and loose joints.

## Prerequisites

Ensure you have:
- Windows 10/11 with **WSL2** and **Ubuntu** installed  
- Python ≥ 3.10  
- Internet connection (to fetch packages)

## Setup

This model must be run in Ubuntu virtual environment:
### 🔹 1. Intall wsl and setup logins
```bash
wsl --install -d Ubuntu-22.04
```
### 🔹 2. In the Linux terminal, install venv (if not already installed)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git wget unzip
```
### 🔹 3. Go to your project folder
```bash
cd /mnt/<Path_to_project_folder>
```
### 🔹 4. Create and activate a virtual environment named .venv
```bash
python3 -m venv .venv
source .venv/bin/activate
```
### 🔹 5. (Optional) Upgrade pip
```bash
pip install --upgrade pip
```
### 🔹 6. Install your dependencies in the requirements.txt file
```bash
pip install -r requirements.txt
```

### 🔹 7. Prepare expected folders (if missing)
```bash
mkdir -p model_weights test_image output_image configs
```
- Put your checkpoint as: model_weights/model.ckpt
- Put a test image as: test_image/test.jpg

### 🔹 8. Run your Python file inside the venv
```bash
python pipeline.py
```


## 2. **Project folders & files you must provide**
   - Place your trained model file in `model_weights/model.ckpt`
   - Ensure configuration file exists at `configs/patchcore_transformers.yaml`
   - test_image/test.jpg                   # any test thermal image you want to try
   - output_image/                         # results will be written here


## 3. Local Image Processing

#### Using the Test Script (Recommended)

```bash
python test_local_inference.py
```

This interactive script will:
- List all available test images
- Let you choose to process one image, all images, or select a specific image
- **Save detection results as JSON files** with coordinates and confidence scores
- Process the image(s) through the complete pipeline
- Save results to the `output_image/` folder
- Display detailed detection results and confidence scores
- **Start file watcher** to auto-update images when JSON files are edited

### Key Functions

#### In `test_local_inference.py` (Local Processing):

**`process_local_test_image(image_filename=None)`**
Processes a test image from the `test_image` folder and saves results to `output_image`.

**Parameters:**
- `image_filename` (str, optional): Name of image file. Defaults to "test.jpg"

**Returns:**
- Dictionary with paths to generated files and detection results

**`list_test_images()`**
Lists all image files in the `test_image` folder.

**Returns:**
- List of image filenames

**`process_all_test_images()`**
Processes all images in the `test_image` folder.

**Returns:**
- Dictionary with results for each processed image

#### In `inference_core.py` (Core Processing):

**`run_pipeline_for_image(image_path)`**
Runs the complete inference pipeline on any image path.

**Parameters:**
- `image_path` (str): Absolute path to image file

**Returns:**
- Dictionary with analysis results and output paths

For each processed image, the following files are generated in `output_image/`:

1. **`labeled/`** - Original image with bounding boxes and labels
2. **`masks/`** - Anomaly heat maps from PatchCore
3. **`filtered/`** - Images showing only anomalous regions
4. **`json/`** - Detection results in JSON format with coordinates and metadata

## 4. JSON Detection Format

Each processed image generates a JSON file with the following structure:

```json
{
  "image_filename": "test.jpg",
  "image_path": "/path/to/test_image/test.jpg",
  "processing_timestamp": "2025-10-02 14:30:15",
  "classification": "Point Overload (Faulty)",
  "total_detections": 2,
  "output_files": {
    "labeled_image": "/path/to/output_image/labeled/test_boxed.png",
    "mask_image": "/path/to/output_image/masks/test_mask.png",
    "filtered_image": "/path/to/output_image/filtered/test_filtered.png"
  },
  "detections": [
    {
      "id": 1,
      "type": "Point Overload (Faulty)",
      "confidence": 0.85,
      "bbox": {
        "x": 150,
        "y": 200, 
        "width": 80,
        "height": 60
      },
      "center": {
        "x": 190,
        "y": 230
      }
    }
  ]
}
```

## 5. Detection Categories

The system can detect and classify:

1. **Point Overload (Faulty)** - Red/orange hotspots indicating immediate attention needed
2. **Point Overload (Potential)** - Yellow hotspots indicating potential issues
3. **Wire Overload** - Extended heated areas along wires or cables
4. **Loose Joint (Faulty/Potential)** - Hotspots in connection areas
5. **Full Wire Overload** - Entire component overheating
6. **Normal** - No significant thermal anomalies detected

Each detection includes:
- Bounding box coordinates `[x, y, width, height]`
- Classification type
- Confidence score (0.0 to 1.0)

## JSON-Based Workflow

### 1. Process Images and Generate JSON
```python
from test_local_inference import process_local_test_image

# Process image and save JSON
result = process_local_test_image("test.jpg", save_json=True)
print(f"JSON saved to: {result['json_path']}")
```

## 6. Edit JSON Files
Open the generated JSON file and modify detection coordinates, types, or confidence scores:
```json
{
  "detections": [
    {
      "id": 1,
      "type": "Point Overload (Faulty)",
      "confidence": 0.90,  // Modified confidence
      "bbox": {
        "x": 155,          // Modified x coordinate
        "y": 205,          // Modified y coordinate  
        "width": 75,       // Modified width
        "height": 55       // Modified height
      }
    }
  ]
}
```

## 7. Auto-Update Images
Start the file watcher to automatically regenerate images when JSON files change:
```python
from test_local_inference import start_json_watcher, stop_json_watcher

# Start watching
observer = start_json_watcher()

# Edit your JSON files - images will auto-update!

# Stop watching (or use Ctrl+C)
stop_json_watcher(observer)
```

## 8. Manual Regeneration
```python
from test_local_inference import regenerate_image_from_json

# Regenerate image from modified JSON
output_path = regenerate_image_from_json("output_image/json/test_detections.json")
print(f"Updated image: {output_path}")
```

## Advanced Usage

### Processing Multiple Images

```python
from test_local_inference import process_all_test_images, list_test_images

# Process all test images
results = process_all_test_images()

# Or process specific images
for image_name in list_test_images():
    if "thermal" in image_name.lower():  # Process only thermal images
        print(f"Processing {image_name}...")
        result = process_local_test_image(image_name)
        print(f"Result: {result['label']}")
```

## 8. Troubleshooting

1. **Model file not found**: Ensure `model_weights/model.ckpt` exists
2. **Config file not found**: Ensure `configs/patchcore_transformers.yaml` exists  
3. **No test images**: Add image files to the `test_image/` folder
4. **Import errors**: Install missing packages with `pip install -r requirements.txt`
5. **CUDA errors**: The system will automatically fall back to CPU if CUDA is unavailable

## 9. Notes

- The system automatically creates output directories if they don't exist
- Cloudinary integration is optional and only used for cloud storage (if needed)
- All local processing works without internet connection
- The model supports GPU acceleration when available but works on CPU as well
