import os
import requests
from tqdm import tqdm

def download_file(url, filename):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as f, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)

def main():
    # Create checkpoints directory if it doesn't exist
    checkpoint_dir = os.path.join('Wav2Lip', 'checkpoints')
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # Download the model
    model_url = 'https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip.pth'
    model_path = os.path.join(checkpoint_dir, 'wav2lip.pth')
    
    if not os.path.exists(model_path):
        print("Downloading Wav2Lip model...")
        download_file(model_url, model_path)
        print("Model downloaded successfully!")
    else:
        print("Model already exists!")

if __name__ == "__main__":
    main() 