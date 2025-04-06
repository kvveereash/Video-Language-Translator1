import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    packages = [
        'pydub',
        'gTTS',
        'SpeechRecognition',
        'ffmpeg-python'
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", package])
            print(f"Successfully installed {package}")
        except Exception as e:
            print(f"Error installing {package}: {e}")
            return False
    return True

if __name__ == "__main__":
    print("Installing required packages...")
    if install_requirements():
        print("\nAll packages installed successfully!")
    else:
        print("\nSome packages failed to install.") 