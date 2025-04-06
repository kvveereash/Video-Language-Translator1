import os
from moviepy.editor import VideoFileClip, AudioFileClip
import subprocess
import torch
import sys

# Add Wav2Lip directory to Python path
wav2lip_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Wav2Lip')
sys.path.append(wav2lip_path)

def extract_audio(video_path):
    """Extract audio from video file."""
    output_path = video_path.rsplit('.', 1)[0] + '.wav'
    
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(output_path, fps=16000, nbytes=2, codec='pcm_s16le')
        audio.close()
        video.close()
        return output_path
    except Exception as e:
        print(f"Error extracting audio: {str(e)}")
        raise

def process_video_with_lipsync(video_path, audio_path, target_language):
    """Process video with Wav2Lip for lip-syncing."""
    output_path = f"output_{target_language}.mp4"
    
    try:
        # Use Wav2Lip inference script
        cmd = [
            'python',
            os.path.join(wav2lip_path, 'inference.py'),
            '--checkpoint_path', os.path.join(wav2lip_path, 'checkpoints', 'wav2lip.pth'),
            '--face', video_path,
            '--audio', audio_path,
            '--outfile', output_path
        ]
        
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error in lip-sync processing: {str(e)}")
        raise
    except Exception as e:
        print(f"Error in lip-sync processing: {str(e)}")
        raise

def combine_audio_video(video_path, audio_path, output_path):
    """Combine processed video with new audio."""
    try:
        # Load video
        video = VideoFileClip(video_path)
        
        # Load audio using AudioFileClip
        audio = AudioFileClip(audio_path)
        
        # Ensure audio duration matches video
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        
        # Combine video with new audio
        final_video = video.set_audio(audio)
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=video.fps
        )
        
        # Clean up
        video.close()
        audio.close()
        
        return output_path
    except Exception as e:
        print(f"Error combining audio and video: {str(e)}")
        raise

def create_video_with_audio(video_path, audio_path, output_path):
    """Create a new video with the translated audio."""
    try:
        # First try lip-sync processing
        try:
            return process_video_with_lipsync(video_path, audio_path, "translated")
        except Exception as e:
            print(f"Lip-sync failed, falling back to simple audio combination: {str(e)}")
            # If lip-sync fails, fall back to simple audio combination
            return combine_audio_video(video_path, audio_path, output_path)
    except Exception as e:
        print(f"Error creating video with audio: {str(e)}")
        raise 