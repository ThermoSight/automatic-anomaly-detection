# JSON Auto-Watch Usage Guide

## Quick Start

1. **Process an image with auto-watch enabled**:
   ```bash
   python test_local_inference.py
   # Choose option 1 (default)
   ```

2. **The script will**:
   - Process your image
   - Save detection results as JSON
   - **Automatically start watching JSON files**
   - **Keep running indefinitely to maintain the watcher**

3. **Edit the JSON file** (in another window/editor):
   - Open `output_image/json/your_image_detections.json` in any text editor
   - Modify bounding box coordinates, confidence scores, or detection types
   - Save the file

4. **See automatic updates**:
   - The labeled image will be regenerated automatically
   - Check `output_image/labeled/your_image_boxed.png` for changes
   - **The script continues watching for more changes**

5. **Stop watching**:
   - Press `Ctrl+C` in the terminal running the script
   - Or run the script again and choose option 5

## How It Works

### Automatic Workflow
```
python test_local_inference.py
  ↓
[Process Image] → [Save JSON] → [Start Watcher] → [Keep Running Indefinitely]
  ↓                               ↓                         ↓
[Edit JSON File] ← ← ← ← ← ← ← ← ← ↓                         ↓
  ↓                               ↓                         ↓
[Auto-Regenerate Image] → → → → → ↓                         ↓
  ↓                               ↓                         ↓
[Check Updated Image] ← ← ← ← ← ← ← ↓                         ↓
  ↓                               ↓                         ↓
[Edit Again...] → → → → → → → → → ↓                         ↓
  ↓                               ↓                         ↓
[Auto-Update Again] ← ← ← ← ← ← ← ← ↓                         ↓
                                  ↓                         ↓
[Continue Watching Forever...] ← ← ↓ ← ← ← ← ← ← ← ← ← ← ← ← ↓
                                                            ↓
[Press Ctrl+C to Stop] → → → → → → → → → → → → → → → → → → → ↓
```

### File Structure After Processing
```
output_image/
├── json/
│   └── test_detections.json      # ← Edit this file
├── labeled/  
│   └── test_boxed.png            # ← This updates automatically
├── masks/
│   └── test_mask.png
└── filtered/
    └── test_filtered.png
```

## JSON Editing Examples

### Change Bounding Box Location
```json
{
  "detections": [
    {
      "bbox": {
        "x": 150,     # ← Change to 160 to move right
        "y": 200,     # ← Change to 210 to move down
        "width": 80,
        "height": 60
      }
    }
  ]
}
```

### Modify Detection Type
```json
{
  "detections": [
    {
      "type": "Point Overload (Potential)",  # ← Change to "Point Overload (Faulty)"
      "confidence": 0.72                     # ← Change to 0.95
    }
  ]
}
```

### Add New Detection
```json
{
  "total_detections": 2,  # ← Update count
  "detections": [
    {
      "id": 1,
      "type": "Point Overload (Faulty)",
      "confidence": 0.85,
      "bbox": {"x": 150, "y": 200, "width": 80, "height": 60}
    },
    {
      "id": 2,  # ← New detection
      "type": "Point Overload (Potential)",
      "confidence": 0.70,
      "bbox": {"x": 300, "y": 350, "width": 60, "height": 45}
    }
  ]
}
```

## Stopping the Watcher

### Method 1: Through Script
```bash
python test_local_inference.py
# Choose option 5: "Stop file watcher and exit"
```

### Method 2: Ctrl+C (if script is running)
- Press `Ctrl+C` in the terminal where the script is running
- The watcher will stop gracefully

### Method 3: Close Terminal
- Closing the terminal will automatically stop the watcher

## Troubleshooting

### Watcher Not Starting
```bash
pip install watchdog
```

### JSON Changes Not Updating Image
1. Check that the JSON file ends with `_detections.json`
2. Ensure the file is in `output_image/json/` folder
3. Wait 1-2 seconds after saving (debounce delay)
4. Check terminal for error messages

### Testing the Watcher
```bash
python test_json_watcher.py
```
This script will:
- Modify a JSON file automatically
- Test if the watcher is working
- Restore the original values

## Advanced Usage

### Process Multiple Images with Watching
```bash
python test_local_inference.py
# Choose option 2: "Process all images"
# Watcher will monitor ALL JSON files
```

### Manual Regeneration (without watcher)
```python
from test_local_inference import regenerate_image_from_json

# Regenerate specific image
regenerate_image_from_json("output_image/json/test_detections.json")
```

### Check if Watcher is Running
Look for these messages in the terminal:
```
[WATCHER] 👁️  Started watching JSON files in: .../output_image/json
[WATCHER] Any changes to *_detections.json files will auto-update images
```

## Benefits

✅ **Real-time editing**: See changes immediately  
✅ **No re-running**: Edit JSON, image updates automatically  
✅ **Batch editing**: Process multiple images, edit any JSON file  
✅ **Precise control**: Modify exact pixel coordinates  
✅ **Data preservation**: All original detection data saved  
✅ **Undo-friendly**: Easy to revert changes in JSON  

## Example Session

```bash
# 1. Process image
python test_local_inference.py
> Choose option 1
> [Image processed, JSON saved, watcher started]
> ⏳ Watching for JSON file changes... (Press Ctrl+C to stop)

# 2. Edit JSON file (in another window/editor)
# Modify output_image/json/test_detections.json
# Save the file

# 3. Check terminal - you'll see:
[WATCHER] JSON file modified: test_detections.json
[WATCHER] Processing changes in: test_detections.json  
[WATCHER] ✅ Image updated successfully: test_boxed.png

# 4. Check the updated image
# output_image/labeled/test_boxed.png now shows your changes!

# 5. Edit JSON again (multiple times)
# Each save will trigger automatic updates
# Script keeps running and watching

# 6. Stop watching
# Press Ctrl+C in the terminal
🛑 Stopping file watcher...
File watcher stopped. Exiting.
```