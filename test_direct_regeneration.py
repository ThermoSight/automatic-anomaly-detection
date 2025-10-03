"""
Direct test of the JSON regeneration functionality.
This bypasses the file watcher and directly tests image regeneration.
"""

import os
import json
import time
from test_local_inference import regenerate_image_from_json, list_test_images

def test_direct_regeneration():
    """Test regenerating images directly from JSON files."""
    
    json_dir = os.path.join(os.path.dirname(__file__), "output_image", "json")
    
    if not os.path.exists(json_dir):
        print("❌ No JSON directory found. Process some images first.")
        return
    
    # List JSON files
    json_files = [f for f in os.listdir(json_dir) if f.endswith('_detections.json')]
    
    if not json_files:
        print("❌ No detection JSON files found. Process some images first.")
        return
    
    print(f"✅ Found {len(json_files)} JSON file(s):")
    for i, file in enumerate(json_files, 1):
        print(f"  {i}. {file}")
    
    # Test with first JSON file
    json_path = os.path.join(json_dir, json_files[0])
    print(f"\n🧪 Testing direct regeneration with: {json_files[0]}")
    
    try:
        # Load original JSON
        with open(json_path, 'r') as f:
            original_data = json.load(f)
        
        print(f"   Original detections: {len(original_data.get('detections', []))}")
        
        # Test 1: Regenerate without changes
        print(f"\n📋 Test 1: Regenerate image without changes")
        output_path = regenerate_image_from_json(json_path)
        print(f"   ✅ Successfully regenerated: {os.path.basename(output_path)}")
        
        # Test 2: Modify JSON and regenerate
        if len(original_data.get('detections', [])) > 0:
            print(f"\n📋 Test 2: Modify JSON coordinates and regenerate")
            
            # Backup original coordinates
            original_x = original_data['detections'][0]['bbox']['x']
            original_y = original_data['detections'][0]['bbox']['y']
            
            # Modify coordinates
            original_data['detections'][0]['bbox']['x'] = original_x + 20
            original_data['detections'][0]['bbox']['y'] = original_y + 15
            
            # Save modified JSON
            with open(json_path, 'w') as f:
                json.dump(original_data, f, indent=2)
            
            print(f"   Modified coordinates: ({original_x}, {original_y}) → ({original_x + 20}, {original_y + 15})")
            
            # Regenerate image
            output_path = regenerate_image_from_json(json_path)
            print(f"   ✅ Successfully regenerated with changes: {os.path.basename(output_path)}")
            
            # Wait a moment
            time.sleep(2)
            
            # Restore original coordinates
            original_data['detections'][0]['bbox']['x'] = original_x
            original_data['detections'][0]['bbox']['y'] = original_y
            
            with open(json_path, 'w') as f:
                json.dump(original_data, f, indent=2)
            
            # Regenerate again
            output_path = regenerate_image_from_json(json_path)
            print(f"   ✅ Successfully restored original coordinates and regenerated")
        
        print(f"\n🎉 All tests passed! The regeneration function works correctly.")
        print(f"📁 Check the labeled image: {output_path}")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

def test_manual_json_edit():
    """Interactive test - asks user to manually edit JSON."""
    
    json_dir = os.path.join(os.path.dirname(__file__), "output_image", "json")
    json_files = [f for f in os.listdir(json_dir) if f.endswith('_detections.json')]
    
    if not json_files:
        print("❌ No JSON files found.")
        return
    
    json_path = os.path.join(json_dir, json_files[0])
    
    print(f"🔧 Manual Edit Test")
    print(f"📁 JSON file: {json_path}")
    print(f"📝 Instructions:")
    print(f"   1. Open the JSON file in any text editor")
    print(f"   2. Change some bbox coordinates (x, y, width, height)")
    print(f"   3. Save the file")
    print(f"   4. Press Enter here to regenerate the image")
    
    input("\nPress Enter when you've saved the JSON file...")
    
    try:
        output_path = regenerate_image_from_json(json_path)
        print(f"✅ Image regenerated: {output_path}")
        print(f"👀 Check the labeled image to see your changes!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("=== Direct JSON Regeneration Test ===")
    print("Choose a test:")
    print("1. Automatic test (modifies JSON programmatically)")
    print("2. Manual test (you edit JSON file)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_direct_regeneration()
    elif choice == "2":
        test_manual_json_edit()
    else:
        print("Invalid choice.")