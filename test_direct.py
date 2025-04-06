import os
from app.utils.video_processor import extract_audio, create_video_with_audio
from app.utils.audio_processor import transcribe_audio, translate_text, generate_speech
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pipeline():
    try:
        # Test video path
        video_path = 'test_video.mp4'
        if not os.path.exists(video_path):
            logger.error("Test video not found!")
            return
        
        logger.info("1. Extracting audio...")
        audio_path = extract_audio(video_path)
        logger.info(f"Audio extracted to: {audio_path}")
        
        logger.info("2. Transcribing audio...")
        transcript = transcribe_audio(audio_path)
        logger.info(f"Transcription: {transcript[:100]}...")
        
        logger.info("3. Translating text...")
        translated_text = translate_text(transcript, 'es')
        logger.info(f"Translation: {translated_text[:100]}...")
        
        logger.info("4. Generating speech...")
        translated_audio_path = generate_speech(translated_text, 'es')
        logger.info(f"Speech generated to: {translated_audio_path}")
        
        logger.info("5. Creating final video...")
        output_path = 'output_direct.mp4'
        final_video = create_video_with_audio(video_path, translated_audio_path, output_path)
        logger.info(f"Final video created at: {final_video}")
        
        # Clean up
        logger.info("Cleaning up temporary files...")
        for path in [audio_path, translated_audio_path]:
            if os.path.exists(path):
                os.remove(path)
        
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    test_pipeline() 
    