import subprocess
import sys

def install_packages():
    packages = [
        'SpeechRecognition',
        'pocketsphinx'
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error installing {package}: {str(e)}")

if __name__ == "__main__":
    install_packages() 