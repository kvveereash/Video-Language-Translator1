import os

def setup_directories():
    """Create necessary directories for the application."""
    directories = [
        'uploads',
        'outputs',
        'temp'
    ]
    
    print("Setting up directories...")
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")

if __name__ == "__main__":
    setup_directories() 