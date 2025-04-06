from gtts import gTTS
import os
from moviepy.editor import AudioFileClip, ColorClip
import numpy as np

def create_test_video():
    """Create a test video with speech."""
    try:
        print("Creating test video...")
        
        # Step 1: Generate speech
        print("Generating audio...")
        text = "Hello, this is a test video for translation. We will translate this speech to another language."
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save audio in the current directory
        audio_path = os.path.join(os.getcwd(), "test_audio.mp3")
        tts.save(audio_path)
        print("Audio generated successfully")
        
        # Step 2: Create a simple color clip
        print("Creating video clip...")
        duration = 10  # seconds
        size = (640, 480)
        # Create a blue background using numpy array
        color_array = np.zeros((size[1], size[0], 3))
        color_array[:, :, 2] = 255  # Blue color
        
        # Create the color clip
        color_clip = ColorClip(size, color=(0, 0, 255), duration=duration)
        
        # Step 3: Load and set audio
        print("Adding audio to video...")
        audio = AudioFileClip(audio_path)
        video = color_clip.set_audio(audio)
        
        # Step 4: Write final video
        print("Saving video file...")
        output_path = os.path.join(os.getcwd(), "test_video.mp4")
        video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Clean up
        print("Cleaning up temporary files...")
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        print("Video created successfully at:", output_path)
        return True
        
    except Exception as e:
        print(f"\nError creating video: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have write permissions in the current directory")
        print("2. Check if ffmpeg is installed correctly")
        print("3. Try running the script with administrator privileges")
        return False

if __name__ == "__main__":
    create_test_video() 