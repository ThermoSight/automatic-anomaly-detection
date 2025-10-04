"""
Quick test to verify file watcher is detecting JSON changes.
Run this while the main script is running with watcher active.
"""

import os
import json
import time

def quick_watcher_test():
    """Quick test to see if watcher detects changes."""
    
    json_dir = os.path.join(os.path.dirname(__file__), "output_image", "json")
    
    if not os.path.exists(json_dir):
        print("❌ No JSON directory found.")
        return
    
    json_files = [f for f in os.listdir(json_dir) if f.endswith('_detections.json')]
    
    if not json_files:
        print("❌ No JSON files found.")
        return
    
    test_file = os.path.join(json_dir, json_files[0])
    
    print(f"🧪 Quick Watcher Test")
    print(f"📁 Testing with: {json_files[0]}")
    print(f"💡 If the main script is running with watcher active,")
    print(f"   you should see [WATCHER] messages when this script modifies the JSON.")
    print(f"\n🔄 Making a small change to trigger the watcher...")
    
    try:
        # Load JSON
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        # Add a timestamp to trigger file change
        data['_test_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save JSON
        with open(test_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ JSON file modified!")
        print(f"👀 Check the terminal running the main script.")
        print(f"   You should see messages like:")
        print(f"   [WATCHER] 🔄 JSON detection file modified: {json_files[0]}")
        print(f"   [WATCHER] ✅ Image updated successfully: ...")
        
        # Wait a moment, then clean up
        time.sleep(3)
        
        # Remove test data
        if '_test_timestamp' in data:
            del data['_test_timestamp']
            with open(test_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"🧹 Cleaned up test data.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    quick_watcher_test()