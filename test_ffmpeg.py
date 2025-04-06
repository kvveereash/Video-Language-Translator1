import ffmpeg

try:
    print("Testing FFmpeg installation...")
    # Try to get FFmpeg version
    probe = ffmpeg.probe('ffmpeg.exe')
    print("FFmpeg is installed correctly!")
except Exception as e:
    print(f"Error: {str(e)}")
    print("Please make sure FFmpeg is installed correctly") 