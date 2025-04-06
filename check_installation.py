import importlib
import subprocess
import sys

def check_package(package_name):
    """Check if a package is installed and get its version."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'Version not found')
        return True, version
    except ImportError:
        return False, None

def check_ffmpeg():
    """Check if ffmpeg is available."""
    try:
        import ffmpeg
        return True
    except ImportError:
        return False

def main():
    packages = {
        'pydub': 'pydub',
        'gTTS': 'gtts',
        'SpeechRecognition': 'speech_recognition',
        'ffmpeg-python': 'ffmpeg'
    }
    
    print("=== Checking Package Installation Status ===\n")
    all_installed = True
    
    for display_name, package_name in packages.items():
        installed, version = check_package(package_name)
        status = "✓ Installed" if installed else "✗ Not installed"
        version_info = f"(version: {version})" if version else ""
        print(f"{display_name}: {status} {version_info}")
        if not installed:
            all_installed = False
    
    print("\n=== Summary ===")
    if all_installed:
        print("All required packages are installed successfully!")
        print("\nYou can now run the speech recognition test using:")
        print("python test_recognition.py")
    else:
        print("Some packages are missing. Please run:")
        print("python setup.py")
        
if __name__ == "__main__":
    main() 