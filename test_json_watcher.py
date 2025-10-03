"""
Simple test script to verify the auto-watch functionality works.
Run this after processing some images to test JSON editing and auto-update.
"""

import os
import json
import time

def test_json_editing():
    """Test the JSON editing and regeneration functionality."""
    
    # Check if we have JSON files
    json_dir = os.path.join(os.path.dirname(__file__), "output_image", "json")
    
    if not os.path.exists(json_dir):
        print("❌ No JSON directory found. Run the main script to process images first.")
        return
    
    # List JSON files
    json_files = [f for f in os.listdir(json_dir) if f.endswith('_detections.json')]
    
    if not json_files:
        print("❌ No detection JSON files found. Process some images first.")
        return
    
    print(f"✅ Found {len(json_files)} JSON file(s):")
    for i, file in enumerate(json_files, 1):
        print(f"  {i}. {file}")
    
    # Test JSON modification
    json_path = os.path.join(json_dir, json_files[0])
    print(f"\n🧪 Testing JSON modification with: {json_files[0]}")
    
    try:
        # Load and modify JSON
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        original_count = len(data.get('detections', []))
        print(f"   Original detections: {original_count}")
        
        if original_count > 0:
            # Modify the first detection's bbox
            detection = data['detections'][0]
            original_x = detection['bbox']['x']
            detection['bbox']['x'] = original_x + 10  # Move box 10 pixels right
            detection['bbox']['y'] = detection['bbox']['y'] + 5  # Move box 5 pixels down
            
            print(f"   Modified first detection: moved box to ({detection['bbox']['x']}, {detection['bbox']['y']})")
            
            # Save modified JSON
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ JSON file modified successfully!")
            print(f"💡 If the file watcher is running, the image should update automatically.")
            print(f"   Check the labeled image to see if the bounding box moved.")
            
            # Wait a moment, then restore original
            time.sleep(3)
            detection['bbox']['x'] = original_x
            detection['bbox']['y'] = detection['bbox']['y'] - 5
            
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"🔄 Restored original coordinates.")
        else:
            print(f"   No detections to modify in this file.")
    
    except Exception as e:
        print(f"❌ Error during JSON test: {str(e)}")


if __name__ == "__main__":
    print("=== JSON Auto-Update Test ===")
    test_json_editing()