# Model Inference for Thermal Image Analysis

This project provides inference capabilities for thermal image analysis using PatchCore anomaly detection. It can detect various types of electrical faults including point overloads, wire overloads, and loose joints.

## Folder Structure

```
Model_Inference/
├── configs/
│   └── patchcore_transformers.yaml    # Model configuration
├── model_weights/
│   └── model.ckpt                     # Pre-trained model weights
├── test_image/
│   └── test.jpg                       # Input test images
├── output_image/
│   ├── masks/                         # Anomaly masks
│   ├── filtered/                      # Filtered images
│   ├── labeled/                       # Final labeled images with bounding boxes
│   └── json/                          # Detection results in JSON format
├── inference_core.py                  # Core inference functions
├── pipeline.py                        # Original pipeline script
├── test_local_inference.py            # Test script for local processing
├── example_detection.json             # Example JSON format
└── requirements.txt                   # Required packages
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Model and Config Files**
   - Place your trained model file in `model_weights/model.ckpt`
   - Ensure configuration file exists at `configs/patchcore_transformers.yaml`

3. **Add Test Images**
   - Place your test images in the `test_image/` folder
   - Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.tif`

## Usage

### Local Image Processing

#### Method 1: Using the Test Script (Recommended)

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

#### Method 2: Using the Local Functions Directly

```python
from test_local_inference import process_local_test_image, list_test_images

# List available test images
images = list_test_images()
print("Available images:", images)

# Process a specific image
result = process_local_test_image("your_image.jpg")

# View results
print(f"Classification: {result['label']}")
print(f"Detected boxes: {len(result['boxes'])}")
for box in result['boxes']:
    print(f"  - {box['type']}: confidence {box['confidence']:.3f}")
```

#### Method 3: Using Core Functions for Custom Processing

```python
from inference_core import run_pipeline_for_image

# Process any image file directly
result = run_pipeline_for_image("/path/to/your/image.jpg")
```

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

## JSON Detection Format

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

### Editing Detection Results

You can manually edit the JSON files to:
- Modify bounding box coordinates (`bbox.x`, `bbox.y`, `bbox.width`, `bbox.height`)
- Change detection types (`type`)
- Adjust confidence scores (`confidence`)
- Add or remove detections

**Auto-Update Feature**: Use the file watcher (option 4 in the script) to automatically regenerate labeled images when you save changes to JSON files.

## Output Files

## Detection Categories

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

## Example Output

```python
{
    'label': 'Point Overload (Faulty)',
    'boxed_path': 'output_image/labeled/test_boxed.png',
    'mask_path': 'output_image/masks/test_mask.png', 
    'filtered_path': 'output_image/filtered/test_filtered.png',
    'json_path': 'output_image/json/test_detections.json',
    'boxes': [
        {
            'box': [150, 200, 80, 60],
            'type': 'Point Overload (Faulty)', 
            'confidence': 0.85
        }
    ]
}
```

## JSON-Based Workflow

### 1. Process Images and Generate JSON
```python
from test_local_inference import process_local_test_image

# Process image and save JSON
result = process_local_test_image("test.jpg", save_json=True)
print(f"JSON saved to: {result['json_path']}")
```

### 2. Edit JSON Files
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

### 3. Auto-Update Images
Start the file watcher to automatically regenerate images when JSON files change:
```python
from test_local_inference import start_json_watcher, stop_json_watcher

# Start watching
observer = start_json_watcher()

# Edit your JSON files - images will auto-update!

# Stop watching (or use Ctrl+C)
stop_json_watcher(observer)
```

### 4. Manual Regeneration
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

### Custom Output Handling

```python
from inference_core import run_pipeline_for_image

# Process image from any location
result = run_pipeline_for_image("/path/to/your/image.jpg")

# Access specific outputs
labeled_image_path = result['boxed_path']
detection_count = len(result['boxes'])
```

## Troubleshooting

1. **Model file not found**: Ensure `model_weights/model.ckpt` exists
2. **Config file not found**: Ensure `configs/patchcore_transformers.yaml` exists  
3. **No test images**: Add image files to the `test_image/` folder
4. **Import errors**: Install missing packages with `pip install -r requirements.txt`
5. **CUDA errors**: The system will automatically fall back to CPU if CUDA is unavailable

## Notes

- The system automatically creates output directories if they don't exist
- Cloudinary integration is optional and only used for cloud storage (if needed)
- All local processing works without internet connection
- The model supports GPU acceleration when available but works on CPU as well