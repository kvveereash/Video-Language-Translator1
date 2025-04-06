import os
import urllib.request
import zipfile
import shutil
import sys

def download_ffmpeg():
    """Download and set up ffmpeg for Windows."""
    print("Setting up ffmpeg...")
    
    # Create temp directory
    if not os.path.exists('temp'):
        os.makedirs('temp')
    
    try:
        # Download ffmpeg
        print("Downloading ffmpeg...")
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = os.path.join('temp', 'ffmpeg.zip')
        
        print("This may take a few minutes...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        # Extract zip
        print("\nExtracting ffmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('temp')
        
        # Find the bin directory
        ffmpeg_dir = None
        for root, dirs, files in os.walk('temp'):
            if 'bin' in dirs:
                ffmpeg_dir = os.path.join(root, 'bin')
                break
        
        if not ffmpeg_dir:
            print("Could not find ffmpeg binaries in the downloaded package")
            return False
        
        # Copy ffmpeg binaries to current directory
        print("\nInstalling ffmpeg...")
        for file in ['ffmpeg.exe', 'ffprobe.exe']:
            src = os.path.join(ffmpeg_dir, file)
            dst = os.path.join(os.getcwd(), file)
            shutil.copy2(src, dst)
            print(f"Installed: {file}")
        
        # Clean up
        print("\nCleaning up...")
        shutil.rmtree('temp')
        
        print("\nffmpeg setup completed successfully!")
        print("You can now run create_test_video.py")
        return True
        
    except Exception as e:
        print(f"\nError during ffmpeg setup: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Make sure you have write permissions in the current directory")
        print("3. Try running the script with administrator privileges")
        return False

if __name__ == "__main__":
    download_ffmpeg() 