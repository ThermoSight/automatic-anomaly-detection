"""
Test script to demonstrate local image processing functionality.
This script shows how to use the updated inference_core.py to process local test images.
"""

import os
import json
import time
import cv2
import numpy as np
import atexit
import signal
from threading import Timer
from inference_core import run_pipeline_for_image

# Global variable to track the file watcher
global_observer = None

# Try to import watchdog, but don't fail if it's not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("[WARNING] Watchdog not available. Install with: pip install watchdog")

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def process_local_test_image(image_filename=None, save_json=True, auto_watch=True):
    """
    Process a test image from the test_image folder locally and save output to output_image folder.
    
    Args:
        image_filename (str, optional): Name of the image file in test_image folder. 
                                       If None, processes 'test.jpg' by default.
        save_json (bool): Whether to save detection results as JSON file.
        auto_watch (bool): Whether to automatically start JSON file watcher.
    
    Returns:
        dict: Results containing paths and analysis results
    """
    if image_filename is None:
        image_filename = "test.jpg"
    
    # Define paths
    test_image_path = os.path.join(BASE_DIR, "test_image", image_filename)
    
    # Check if the test image exists
    if not os.path.exists(test_image_path):
        raise FileNotFoundError(f"Test image not found at {test_image_path}")
    
    print(f"[INFO] Processing local test image: {test_image_path}")
    
    # Run the complete pipeline
    result = run_pipeline_for_image(test_image_path)
    
    # Save JSON if requested
    if save_json:
        json_path = save_detection_json(image_filename, result)
        result['json_path'] = json_path
        print(f"[INFO] Detection results saved to: {json_path}")
    
    print(f"[INFO] Processing completed. Results saved to output_image folder.")
    print(f"[INFO] Classification: {result['label']}")
    print(f"[INFO] Boxes detected: {len(result['boxes'])}")
    
    # Auto-start watcher if requested and JSON was saved
    if auto_watch and save_json and WATCHDOG_AVAILABLE:
        if not global_observer:
            print(f"[INFO] Starting automatic JSON file watcher...")
            watcher_started = start_json_watcher()
            if watcher_started:
                print(f"[INFO] 👁️  File watcher is active! Edit JSON files to update images automatically.")
            else:
                print(f"[WARNING] Failed to start file watcher.")
        else:
            print(f"[INFO] 👁️  File watcher already running.")
    elif auto_watch and save_json and not WATCHDOG_AVAILABLE:
        print(f"[WARNING] Auto-watch requested but watchdog not available.")
        print(f"[WARNING] Install with: pip install watchdog")
    
    return result


def list_test_images():
    """
    List all available test images in the test_image folder.
    
    Returns:
        list: List of image filenames in the test_image folder
    """
    test_image_dir = os.path.join(BASE_DIR, "test_image")
    
    if not os.path.exists(test_image_dir):
        print(f"[WARNING] Test image directory not found: {test_image_dir}")
        return []
    
    # Common image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    image_files = []
    for file in os.listdir(test_image_dir):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    return sorted(image_files)


def save_detection_json(image_filename, result):
    """
    Save detection results to a JSON file.
    
    Args:
        image_filename (str): Name of the processed image
        result (dict): Detection results from the pipeline
    
    Returns:
        str: Path to the saved JSON file
    """
    # Create JSON output directory
    json_dir = os.path.join(BASE_DIR, "output_image", "json")
    os.makedirs(json_dir, exist_ok=True)
    
    # Generate JSON filename
    base_name = os.path.splitext(image_filename)[0]
    json_filename = f"{base_name}_detections.json"
    json_path = os.path.join(json_dir, json_filename)
    
    # Prepare JSON data
    json_data = {
        "image_filename": image_filename,
        "image_path": os.path.join(BASE_DIR, "test_image", image_filename),
        "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "classification": result['label'],
        "total_detections": len(result['boxes']),
        "output_files": {
            "labeled_image": result['boxed_path'],
            "mask_image": result.get('mask_path'),
            "filtered_image": result.get('filtered_path')
        },
        "detections": []
    }
    
    # Add detection details
    for i, box_info in enumerate(result['boxes']):
        detection = {
            "id": i + 1,
            "type": box_info['type'],
            "confidence": box_info['confidence'],
            "bbox": {
                "x": box_info['box'][0],
                "y": box_info['box'][1], 
                "width": box_info['box'][2],
                "height": box_info['box'][3]
            },
            "center": {
                "x": box_info['box'][0] + box_info['box'][2] // 2,
                "y": box_info['box'][1] + box_info['box'][3] // 2
            }
        }
        json_data["detections"].append(detection)
    
    # Save JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return json_path


def load_detection_json(json_path):
    """
    Load detection results from a JSON file.
    
    Args:
        json_path (str): Path to the JSON file
    
    Returns:
        dict: Detection data from JSON
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Error loading JSON file: {str(e)}")


def regenerate_image_from_json(json_path):
    """
    Regenerate labeled image based on JSON detection data.
    
    Args:
        json_path (str): Path to the JSON file containing detection data
    
    Returns:
        str: Path to the regenerated labeled image
    """
    print(f"[REGEN] Starting regeneration from: {json_path}")
    
    # Load JSON data
    print(f"[REGEN] Loading JSON data...")
    json_data = load_detection_json(json_path)
    print(f"[REGEN] JSON loaded successfully. Found {len(json_data.get('detections', []))} detection(s)")
    
    # Load original image
    original_image_path = json_data['image_path']
    print(f"[REGEN] Original image path: {original_image_path}")
    
    if not os.path.exists(original_image_path):
        raise FileNotFoundError(f"Original image not found: {original_image_path}")
    
    # Load image
    print(f"[REGEN] Loading original image...")
    img = cv2.imread(original_image_path)
    if img is None:
        raise ValueError(f"Could not load image: {original_image_path}")
    
    print(f"[REGEN] Image loaded. Shape: {img.shape}")
    print(f"[REGEN] Regenerating image from JSON: {json_path}")
    print(f"[REGEN] Found {len(json_data['detections'])} detection(s) in JSON")
    
    # Draw boxes based on JSON data
    for i, detection in enumerate(json_data['detections']):
        bbox = detection['bbox']
        x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
        print(f"[REGEN] Drawing detection {i+1}: {detection['type']} at ({x}, {y}, {w}, {h})")
        
        # Draw rectangle
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # Prepare text
        text = f"{detection['type']} ({detection['confidence']:.2f})"
        
        # Draw text background
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x, max(0, y - text_height - 10)), 
                     (x + text_width, y), (0, 0, 255), -1)
        
        # Draw text
        cv2.putText(img, text, (x, max(text_height, y - 10)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # If no detections, add classification label
    if len(json_data['detections']) == 0:
        print(f"[REGEN] No detections found, adding classification label: {json_data['classification']}")
        cv2.putText(img, json_data['classification'], (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    # Generate output path
    image_filename = json_data['image_filename']
    base_name = os.path.splitext(image_filename)[0]
    output_path = os.path.join(BASE_DIR, "output_image", "labeled", f"{base_name}_boxed.png")
    
    print(f"[REGEN] Output path: {output_path}")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save regenerated image
    print(f"[REGEN] Saving regenerated image...")
    success = cv2.imwrite(output_path, img)
    if not success:
        raise ValueError(f"Failed to save regenerated image: {output_path}")
    
    print(f"[REGEN] ✅ Regenerated labeled image saved: {output_path}")
    return output_path


def start_json_watcher():
    """
    Start watching JSON files for changes and auto-regenerate images.
    
    Returns:
        Observer: The file system observer (for stopping later)
    """
    global global_observer
    
    if not WATCHDOG_AVAILABLE:
        print(f"[WATCHER] ❌ Watchdog not available. Install with: pip install watchdog")
        return False
    
    # Stop existing watcher if running
    if global_observer:
        stop_json_watcher()
    
    json_dir = os.path.join(BASE_DIR, "output_image", "json")
    
    if not os.path.exists(json_dir):
        print(f"[WATCHER] Creating JSON directory: {json_dir}")
        os.makedirs(json_dir, exist_ok=True)
    
    try:
        # Create handler that inherits from FileSystemEventHandler
        if WATCHDOG_AVAILABLE:
            class JSONHandler(FileSystemEventHandler):
                def __init__(self):
                    super().__init__()
                    self.debounce_timers = {}
                    self.debounce_delay = 0.5  # Reduced from 1.0 to 0.5 seconds for faster response
                
                def on_modified(self, event):
                    self._handle_file_event(event, "modified")
                
                def on_moved(self, event):
                    self._handle_file_event(event, "moved")
                
                def on_created(self, event):
                    self._handle_file_event(event, "created")
                
                def _handle_file_event(self, event, event_type):
                    if event.is_directory:
                        return
                    
                    file_path = event.src_path
                    print(f"[WATCHER] File {event_type}: {os.path.basename(file_path)}")
                    
                    if not file_path.endswith('_detections.json'):
                        print(f"[WATCHER] Ignoring non-detection file: {os.path.basename(file_path)}")
                        return
                    
                    print(f"[WATCHER] 🔄 JSON detection file {event_type}: {os.path.basename(file_path)}")
                    
                    # Cancel existing timer for this file
                    if file_path in self.debounce_timers:
                        self.debounce_timers[file_path].cancel()
                        print(f"[WATCHER] Cancelled previous timer for: {os.path.basename(file_path)}")
                    
                    # Set new timer with debounce
                    timer = Timer(self.debounce_delay, self._process_json_change, [file_path])
                    self.debounce_timers[file_path] = timer
                    timer.start()
                    print(f"[WATCHER] Started {self.debounce_delay}s debounce timer for: {os.path.basename(file_path)}")
                
                def _process_json_change(self, json_path):
                    """Process the JSON file change after debounce delay."""
                    try:
                        print(f"[WATCHER] 🔄 Processing changes in: {os.path.basename(json_path)}")
                        print(f"[WATCHER] Calling regenerate_image_from_json...")
                        output_path = regenerate_image_from_json(json_path)
                        print(f"[WATCHER] ✅ Image updated successfully: {os.path.basename(output_path)}")
                        print(f"[WATCHER] Updated image path: {output_path}")
                    except Exception as e:
                        print(f"[WATCHER] ❌ Error processing JSON change: {str(e)}")
                        import traceback
                        print(f"[WATCHER] Full error traceback:")
                        traceback.print_exc()
                    finally:
                        # Clean up timer
                        if json_path in self.debounce_timers:
                            del self.debounce_timers[json_path]
                            print(f"[WATCHER] Cleaned up timer for: {os.path.basename(json_path)}")
            
            event_handler = JSONHandler()
        else:
            return False
        
        global_observer = Observer()
        global_observer.schedule(event_handler, json_dir, recursive=False)
        global_observer.start()
        
        print(f"[WATCHER] 👁️  Started watching JSON files in: {json_dir}")
        print(f"[WATCHER] Any changes to *_detections.json files will auto-update images")
        return True
        
    except Exception as e:
        print(f"[WATCHER] ❌ Failed to start file watcher: {str(e)}")
        global_observer = None
        return False


def stop_json_watcher(observer=None):
    """
    Stop the JSON file watcher.
    
    Args:
        observer: The Observer instance to stop (optional, uses global if not provided)
    """
    global global_observer
    
    target_observer = observer or global_observer
    
    if target_observer:
        try:
            target_observer.stop()
            target_observer.join()
            print(f"[WATCHER] 🛑 Stopped watching JSON files")
        except Exception as e:
            print(f"[WATCHER] Error stopping watcher: {str(e)}")
        finally:
            if target_observer == global_observer:
                global_observer = None


def cleanup_watcher():
    """Cleanup function to stop watcher on exit."""
    stop_json_watcher()


# Register cleanup function
atexit.register(cleanup_watcher)

# Handle Ctrl+C gracefully
def signal_handler(sig, frame):
    print(f"\n[INFO] Received interrupt signal. Cleaning up...")
    cleanup_watcher()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)


def process_all_test_images(save_json=True, auto_watch=True):
    """
    Process all test images in the test_image folder.
    
    Args:
        save_json (bool): Whether to save detection results as JSON files.
        auto_watch (bool): Whether to automatically start JSON file watcher.
    
    Returns:
        dict: Results for each processed image
    """
    test_images = list_test_images()
    
    if not test_images:
        print("No test images found to process.")
        return {}
    
    results = {}
    print(f"\nProcessing {len(test_images)} test image(s)...")
    
    for i, image_name in enumerate(test_images, 1):
        print(f"\n[{i}/{len(test_images)}] Processing: {image_name}")
        try:
            # For the first image, start auto_watch. For subsequent images, don't restart watcher
            should_auto_watch = auto_watch and i == 1
            result = process_local_test_image(image_name, save_json=save_json, auto_watch=should_auto_watch)
            results[image_name] = result
            print(f"    ✅ Success: {result['label']}")
            if save_json and 'json_path' in result:
                print(f"    📄 JSON saved: {os.path.basename(result['json_path'])}")
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            results[image_name] = {"error": str(e)}
    
    # Show watcher status after processing all images
    if auto_watch and save_json and len(results) > 0:
        if WATCHDOG_AVAILABLE and global_observer:
            print(f"\n[INFO] 👁️  File watcher is active for all processed images!")
            print(f"[INFO] Edit any JSON file to automatically update the corresponding image.")
        elif not WATCHDOG_AVAILABLE:
            print(f"\n[WARNING] Install watchdog to enable auto-update: pip install watchdog")
    
    return results


def display_results_summary(results):
    """
    Display a summary of processing results.
    
    Args:
        results (dict): Results from process_all_test_images()
    """
    if not results:
        return
    
    print(f"\n{'='*60}")
    print("PROCESSING SUMMARY")
    print(f"{'='*60}")
    
    successful = 0
    failed = 0
    
    for image_name, result in results.items():
        if "error" in result:
            print(f"❌ {image_name}: FAILED - {result['error']}")
            failed += 1
        else:
            box_count = len(result.get('boxes', []))
            print(f"✅ {image_name}: {result['label']} ({box_count} detections)")
            successful += 1
    
    print(f"\nTotal: {len(results)} images processed")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        print(f"\n📁 Output files saved in:")
        print(f"   - output_image/labeled/   (final images with bounding boxes)")
        print(f"   - output_image/masks/     (anomaly heat maps)")
        print(f"   - output_image/filtered/  (filtered anomaly regions)")


def main():
    """Main function to test local image processing"""
    print("=== Local Image Processing Test ===")
    print("📄 JSON export and 👁️  auto-watching enabled by default!")
    
    # List available test images
    print("\n1. Listing available test images:")
    test_images = list_test_images()
    
    if not test_images:
        print("No test images found in the test_image folder.")
        print("Please add some image files (.jpg, .png, etc.) to the test_image folder.")
        return
    
    print(f"Found {len(test_images)} test image(s):")
    for i, img in enumerate(test_images, 1):
        print(f"  {i}. {img}")
    
    # Ask user what they want to do
    print(f"\nWhat would you like to do?")
    print(f"1. Process one image (with JSON export + auto-watch)")
    print(f"2. Process all images (with JSON export + auto-watch)")  
    print(f"3. Choose specific image to process")
    print(f"4. Regenerate image from existing JSON file")
    print(f"5. Stop file watcher and exit")
    print(f"\n💡 Note: After processing, the script will keep running to watch for JSON changes.")
    print(f"   Edit JSON files and see images update automatically!")
    print(f"   Press Ctrl+C anytime to stop watching.")
    
    try:
        choice = input("\nEnter choice (1-5) [default: 1]: ").strip()
        if not choice:
            choice = "1"
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        cleanup_watcher()
        return
    
    try:
        if choice == "1":
            # Process default image
            if "test.jpg" in test_images:
                image_to_process = "test.jpg"
            else:
                image_to_process = test_images[0]
            
            print(f"\n2. Processing: {image_to_process}")
            result = process_local_test_image(image_to_process, save_json=True, auto_watch=True)
            
            # Display detailed results
            print(f"\n3. Results:")
            print(f"   Classification: {result['label']}")
            print(f"   Detected boxes: {len(result['boxes'])}")
            print(f"   Output files:")
            print(f"     - Labeled image: {result['boxed_path']}")
            if 'json_path' in result:
                print(f"     - Detection JSON: {result['json_path']}")
            if result['mask_path']:
                print(f"     - Anomaly mask: {result['mask_path']}")
            if result['filtered_path']:
                print(f"     - Filtered image: {result['filtered_path']}")
            
            if result['boxes']:
                print(f"\n   Detection details:")
                for i, box in enumerate(result['boxes'], 1):
                    print(f"     Box {i}: {box['type']} (confidence: {box['confidence']:.3f})")
                    print(f"             Location: {box['box']}")
            
            print(f"\n✅ Processing completed successfully!")
            
            if global_observer:
                print(f"\n💡 The file watcher is now active!")
                print(f"   📝 Edit the JSON file to modify detections")
                print(f"   🔄 Images will update automatically when you save changes")
                print(f"   🛑 Press Ctrl+C to stop watching and exit")
                
                # Keep the script running to maintain the watcher
                try:
                    print(f"\n⏳ Watching for JSON file changes... (Press Ctrl+C to stop)")
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print(f"\n\n🛑 Stopping file watcher...")
                    stop_json_watcher()
                    print(f"File watcher stopped. Exiting.")
                    return
        
        elif choice == "2":
            # Process all images
            print(f"\n2. Processing all images...")
            results = process_all_test_images(save_json=True, auto_watch=True)
            display_results_summary(results)
            
            if global_observer:
                print(f"\n💡 The file watcher is now active for all processed images!")
                print(f"   📝 Edit any JSON file to modify detections")
                print(f"   🔄 Images will update automatically when you save changes")
                print(f"   🛑 Press Ctrl+C to stop watching and exit")
                
                # Keep the script running to maintain the watcher
                try:
                    print(f"\n⏳ Watching for JSON file changes... (Press Ctrl+C to stop)")
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print(f"\n\n🛑 Stopping file watcher...")
                    stop_json_watcher()
                    print(f"File watcher stopped. Exiting.")
                    return
        
        elif choice == "3":
            # Choose specific image
            print(f"\nAvailable images:")
            for i, img in enumerate(test_images, 1):
                print(f"  {i}. {img}")
            
            try:
                img_choice = int(input(f"\nChoose image (1-{len(test_images)}): ")) - 1
                if 0 <= img_choice < len(test_images):
                    image_to_process = test_images[img_choice]
                    print(f"\n2. Processing: {image_to_process}")
                    result = process_local_test_image(image_to_process, save_json=True, auto_watch=True)
                    
                    print(f"\n3. Results:")
                    print(f"   Classification: {result['label']}")
                    print(f"   Detected boxes: {len(result['boxes'])}")
                    print(f"   Output saved to: {result['boxed_path']}")
                    if 'json_path' in result:
                        print(f"   JSON saved to: {result['json_path']}")
                    print(f"\n✅ Processing completed successfully!")
                    
                    if global_observer:
                        print(f"\n💡 File watcher is active! Edit the JSON to update the image.")
                        print(f"   🛑 Press Ctrl+C to stop watching and exit")
                        
                        # Keep the script running to maintain the watcher
                        try:
                            print(f"\n⏳ Watching for JSON file changes... (Press Ctrl+C to stop)")
                            while True:
                                time.sleep(1)
                        except KeyboardInterrupt:
                            print(f"\n\n🛑 Stopping file watcher...")
                            stop_json_watcher()
                            print(f"File watcher stopped. Exiting.")
                            return
                else:
                    print("Invalid choice.")
                    return
            except (ValueError, IndexError):
                print("Invalid input.")
                return
        
        elif choice == "4":
            # Regenerate from JSON
            json_dir = os.path.join(BASE_DIR, "output_image", "json")
            if not os.path.exists(json_dir):
                print("No JSON files found. Process some images first.")
                return
            
            # List available JSON files
            json_files = [f for f in os.listdir(json_dir) if f.endswith('_detections.json')]
            if not json_files:
                print("No detection JSON files found. Process some images first.")
                return
            
            print(f"\nAvailable detection JSON files:")
            for i, json_file in enumerate(json_files, 1):
                print(f"  {i}. {json_file}")
            
            try:
                json_choice = int(input(f"\nChoose JSON file (1-{len(json_files)}): ")) - 1
                if 0 <= json_choice < len(json_files):
                    json_file = json_files[json_choice]
                    json_path = os.path.join(json_dir, json_file)
                    
                    print(f"\n2. Regenerating image from: {json_file}")
                    output_path = regenerate_image_from_json(json_path)
                    print(f"✅ Image regenerated: {os.path.basename(output_path)}")
                    
                    # Start watcher if not already running
                    if not global_observer and WATCHDOG_AVAILABLE:
                        print(f"[INFO] Starting file watcher for future edits...")
                        start_json_watcher()
                        print(f"💡 File watcher is now active!")
                        
                        # Keep the script running to maintain the watcher
                        try:
                            print(f"\n⏳ Watching for JSON file changes... (Press Ctrl+C to stop)")
                            while True:
                                time.sleep(1)
                        except KeyboardInterrupt:
                            print(f"\n\n🛑 Stopping file watcher...")
                            stop_json_watcher()
                            print(f"File watcher stopped. Exiting.")
                            return
                else:
                    print("Invalid choice.")
                    return
            except (ValueError, IndexError):
                print("Invalid input.")
                return
        
        elif choice == "5":
            # Stop watcher and exit
            if global_observer:
                print(f"\nStopping file watcher...")
                stop_json_watcher()
                print(f"File watcher stopped. Exiting.")
            else:
                print(f"\nNo file watcher running. Exiting.")
            return
        
        else:
            print("Invalid choice.")
            return
        
        print(f"\nCheck the 'output_image' folder for all results.")
        print(f"Run the script again to process more images or stop the watcher.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Don't automatically stop watcher here - let it run for auto-updates
        pass


if __name__ == "__main__":
    main()