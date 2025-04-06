from celery import Task, chain
from app import celery
from app.utils.video_processor import extract_audio, create_video_with_audio
from app.utils.audio_processor import transcribe_audio, translate_text, generate_speech
import os
import tempfile
import shutil
import yt_dlp
import logging
import time
from speech_recognition import UnknownValueError, RequestError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")
        logger.error(f"Error info: {einfo}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

@celery.task(bind=True, base=TranslationTask)
def process_video(self, video_path, target_language):
    """Process video for translation."""
    try:
        logger.info(f"Starting video processing: {video_path}")
        
        # Create output directory if it doesn't exist
        os.makedirs('outputs', exist_ok=True)
        
        # Extract audio from video
        self.update_state(state='PROGRESS', meta={'status': 'Extracting audio...'})
        logger.info("Extracting audio from video")
        audio_path = extract_audio(video_path)
        
        # Transcribe audio to text
        self.update_state(state='PROGRESS', meta={'status': 'Transcribing audio...'})
        logger.info("Transcribing audio to text")
        try:
            transcript = transcribe_audio(audio_path)
            if not transcript:
                raise ValueError("No speech detected in the video")
            logger.info(f"Transcription result: {transcript[:100]}...")
        except UnknownValueError:
            logger.error("Speech recognition failed to understand the audio")
            raise ValueError("Could not understand the speech in the video. Please ensure the audio is clear and in a supported language.")
        except RequestError as e:
            logger.error(f"Speech recognition service error: {str(e)}")
            raise ValueError("Speech recognition service is currently unavailable. Please try again later.")
        
        # Translate text
        self.update_state(state='PROGRESS', meta={'status': 'Translating text...'})
        logger.info(f"Translating text to {target_language}")
        translated_text = translate_text(transcript, target_language)
        logger.info(f"Translation result: {translated_text[:100]}...")
        
        # Generate speech from translated text
        self.update_state(state='PROGRESS', meta={'status': 'Generating speech...'})
        logger.info("Generating speech from translated text")
        translated_audio_path = generate_speech(translated_text, target_language)
        
        # Create video with translated audio
        self.update_state(state='PROGRESS', meta={'status': 'Creating final video...'})
        logger.info("Creating final video with translated audio")
        output_path = os.path.join('outputs', f'{self.request.id}.mp4')
        create_video_with_audio(video_path, translated_audio_path, output_path)
        
        # Clean up temporary files
        logger.info("Cleaning up temporary files")
        for path in [audio_path, translated_audio_path]:
            if os.path.exists(path):
                os.remove(path)
        
        logger.info("Video processing completed successfully")
        return {'status': 'success', 'video_path': output_path}
        
    except Exception as e:
        logger.error(f"Error during video processing: {str(e)}", exc_info=True)
        # Clean up any temporary files
        try:
            if 'audio_path' in locals() and os.path.exists(audio_path):
                os.remove(audio_path)
            if 'translated_audio_path' in locals() and os.path.exists(translated_audio_path):
                os.remove(translated_audio_path)
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {str(cleanup_error)}")
        
        return {'status': 'error', 'message': str(e)}

@celery.task(bind=True, base=TranslationTask)
def process_youtube_video(self, youtube_url, target_language):
    """Process YouTube video for translation."""
    try:
        # Download YouTube video
        self.update_state(state='PROGRESS', meta={'status': 'Downloading YouTube video...'})
        logger.info(f"Processing YouTube URL: {youtube_url}")
        
        # Create temporary directory that persists until we're done
        temp_dir = tempfile.mkdtemp()
        try:
            video_path = None
            try:
                # Download the video
                video_path = download_youtube_video(youtube_url, temp_dir)
                logger.info(f"YouTube video downloaded to: {video_path}")
                
                # Process the video directly
                self.update_state(state='PROGRESS', meta={'status': 'Processing video...'})
                
                # Create output directory if it doesn't exist
                os.makedirs('outputs', exist_ok=True)
                
                # Extract audio from video
                self.update_state(state='PROGRESS', meta={'status': 'Extracting audio...'})
                logger.info("Extracting audio from video")
                audio_path = extract_audio(video_path)
                
                # Transcribe audio to text
                self.update_state(state='PROGRESS', meta={'status': 'Transcribing audio...'})
                logger.info("Transcribing audio to text")
                transcript = transcribe_audio(audio_path)
                
                # Handle case where there's minimal or no speech
                if transcript == "[Background music or minimal speech detected]":
                    logger.info("Video contains minimal or no speech")
                    return {
                        'status': 'info',
                        'message': 'This video appears to have minimal or no speech to translate. Please try a video with more dialogue.'
                    }
                
                logger.info(f"Transcription result: {transcript[:100]}...")
                
                # Translate text
                self.update_state(state='PROGRESS', meta={'status': 'Translating text...'})
                logger.info(f"Translating text to {target_language}")
                translated_text = translate_text(transcript, target_language)
                logger.info(f"Translation result: {translated_text[:100]}...")
                
                # Generate speech from translated text
                self.update_state(state='PROGRESS', meta={'status': 'Generating speech...'})
                logger.info("Generating speech from translated text")
                translated_audio_path = generate_speech(translated_text, target_language)
                
                # Create video with translated audio
                self.update_state(state='PROGRESS', meta={'status': 'Creating final video...'})
                logger.info("Creating final video with translated audio")
                output_path = os.path.join('outputs', f'{self.request.id}.mp4')
                create_video_with_audio(video_path, translated_audio_path, output_path)
                
                # Clean up temporary files
                logger.info("Cleaning up temporary files")
                for path in [audio_path, translated_audio_path]:
                    if os.path.exists(path):
                        os.remove(path)
                
                logger.info("Video processing completed successfully")
                return {'status': 'success', 'video_path': output_path}
                
            except Exception as e:
                logger.error(f"Error processing YouTube video: {str(e)}", exc_info=True)
                error_msg = str(e)
                if "minimal or no speech" in error_msg:
                    return {
                        'status': 'info',
                        'message': 'This video appears to have minimal or no speech to translate. Please try a video with more dialogue.'
                    }
                return {'status': 'error', 'message': error_msg}
                
            finally:
                # Clean up the downloaded video in the finally block
                if video_path and os.path.exists(video_path):
                    try:
                        os.remove(video_path)
                        logger.info(f"Cleaned up temporary video file: {video_path}")
                    except Exception as cleanup_error:
                        logger.error(f"Error cleaning up temporary file: {str(cleanup_error)}")
                        
        finally:
            # Clean up the temporary directory
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up temporary directory: {str(cleanup_error)}")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"YouTube processing error: {error_msg}")
        return {'status': 'error', 'message': error_msg}

def download_youtube_video(youtube_url, output_dir):
    """Download YouTube video to the specified directory using yt-dlp."""
    try:
        logger.info(f"Attempting to download video from URL: {youtube_url}")
        
        # Clean and validate the URL
        if not youtube_url or not isinstance(youtube_url, str):
            raise ValueError("Invalid YouTube URL")
            
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]',  # Best quality MP4
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'logger': logger,
            'socket_timeout': 30,  # Timeout in seconds
            'retries': 3,  # Number of retries
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'ignoreerrors': True
        }
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # First, try to extract info to verify the video is accessible
                info = ydl.extract_info(youtube_url, download=False)
                logger.info(f"Successfully found video: {info.get('title', 'Unknown title')}")
                
                # If video info was retrieved successfully, proceed with download
                info = ydl.extract_info(youtube_url, download=True)
                video_path = ydl.prepare_filename(info)
                
                if not os.path.exists(video_path):
                    raise Exception("Video download failed - file not found")
                    
                logger.info(f"Video downloaded successfully to: {video_path}")
                return video_path
                
            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e).lower()
                if "copyright" in error_msg:
                    raise Exception("Cannot process copyrighted content")
                elif "private" in error_msg:
                    raise Exception("Cannot process private videos")
                elif "not available" in error_msg:
                    raise Exception("This video is not available")
                else:
                    raise Exception(f"Failed to download video: {str(e)}")
                    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"YouTube download error: {error_msg}", exc_info=True)
        raise Exception(f"Failed to download YouTube video: {error_msg}") 