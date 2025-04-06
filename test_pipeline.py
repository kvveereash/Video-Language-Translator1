import os
import requests
import time
from pprint import pprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print API keys (masked for security)
print("\n=== Environment Variables ===")
print(f"ELEVENLABS_API_KEY: {'*' * 8}{os.getenv('ELEVENLABS_API_KEY')[-4:] if os.getenv('ELEVENLABS_API_KEY') else 'Not set'}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or 'Not set'}")

def test_video_upload():
    """Test uploading a video file for translation."""
    print("\n=== Testing Video Upload ===")
    
    # API endpoint
    url = 'http://localhost:5000/api/upload'
    
    # Test video path
    video_path = 'test_video.mp4'
    if not os.path.exists(video_path):
        print("Test video not found. Please provide a test video file.")
        return None
    
    # Parameters for translation
    data = {
        'target_language': 'es'  # Spanish
    }
    
    # Upload video file
    try:
        with open(video_path, 'rb') as video_file:
            files = {
                'video': video_file
            }
            print("Uploading video...")
            response = requests.post(url, data=data, files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("Upload successful!")
                print(f"Task ID: {result.get('task_id')}")
                return result.get('task_id')
            else:
                print(f"Upload failed with status code: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
    except Exception as e:
        print(f"Error during upload: {str(e)}")
        return None

def check_translation_status(task_id):
    """Check the status of a translation task."""
    print(f"\n=== Checking Translation Status for Task {task_id} ===")
    
    url = f'http://localhost:5000/api/status/{task_id}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Status check failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error checking status: {str(e)}")
        return None

def download_translated_video(task_id):
    """Download the translated video."""
    print("\n=== Downloading Translated Video ===")
    
    url = f'http://localhost:5000/api/download/{task_id}'
    output_path = 'translated_video.mp4'
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Video downloaded successfully to: {output_path}")
            return True
        else:
            print(f"Download failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return False

def test_complete_pipeline():
    """Test the complete video translation pipeline."""
    print("=== Starting Complete Pipeline Test ===")
    
    # Step 1: Upload video
    task_id = test_video_upload()
    if not task_id:
        print("Pipeline test failed at video upload stage")
        return False
    
    # Step 2: Monitor translation progress
    max_attempts = 30  # Maximum number of status checks
    attempt = 0
    
    while attempt < max_attempts:
        status = check_translation_status(task_id)
        if not status:
            print("Pipeline test failed at status check stage")
            return False
        
        print(f"\nCurrent Status: {status.get('state')}")
        print("Progress:")
        pprint(status)
        
        if status.get('state') == 'SUCCESS':
            break
        elif status.get('state') == 'FAILURE':
            print(f"Translation failed: {status.get('error')}")
            return False
        
        attempt += 1
        print("\nWaiting 10 seconds before next status check...")
        time.sleep(10)
    
    if attempt >= max_attempts:
        print("Pipeline test timed out")
        return False
    
    # Step 3: Download translated video
    success = download_translated_video(task_id)
    if not success:
        print("Pipeline test failed at download stage")
        return False
    
    print("\n=== Pipeline Test Summary ===")
    print("✓ Video upload successful")
    print("✓ Translation processing completed")
    print("✓ Video download successful")
    print("\nComplete pipeline test passed successfully!")
    return True

if __name__ == "__main__":
    test_complete_pipeline() 