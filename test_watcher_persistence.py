"""
Quick test to verify the file watcher persistence.
This script will continuously show watcher status.
"""

import os
import time
import json

def monitor_watcher_status():
    """Monitor if the watcher is actively responding to changes."""
    
    json_dir = os.path.join(os.path.dirname(__file__), "output_image", "json")
    
    if not os.path.exists(json_dir):
        print("❌ No JSON directory found.")
        return
    
    json_files = [f for f in os.listdir(json_dir) if f.endswith('_detections.json')]
    
    if not json_files:
        print("❌ No JSON files found. Process some images first.")
        return
    
    test_file = os.path.join(json_dir, json_files[0])
    
    print(f"🧪 Testing watcher with: {json_files[0]}")
    print(f"💡 If watcher is active, you should see updates when this script modifies the JSON.")
    print(f"🛑 Press Ctrl+C to stop\n")
    
    counter = 0
    
    try:
        while True:
            counter += 1
            
            # Load JSON
            with open(test_file, 'r') as f:
                data = json.load(f)
            
            # Add a test comment to trigger file change
            data['_test_modification'] = f"Auto-test #{counter} at {time.strftime('%H:%M:%S')}"
            
            # Save JSON
            with open(test_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"[{time.strftime('%H:%M:%S')}] Test #{counter}: Modified JSON file")
            print("   → If watcher is active, you should see '[WATCHER]' messages")
            
            # Wait before next test
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Test stopped.")
        
        # Clean up test data
        try:
            with open(test_file, 'r') as f:
                data = json.load(f)
            
            if '_test_modification' in data:
                del data['_test_modification']
                
                with open(test_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"🧹 Cleaned up test data from JSON file.")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

if __name__ == "__main__":
    print("=== File Watcher Persistence Test ===")
    monitor_watcher_status()