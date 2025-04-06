import os
import speech_recognition as sr
from google.cloud import translate_v2 as translate
import google.cloud.texttospeech as texttospeech
from gtts import gTTS
import tempfile
import soundfile as sf
import logging
import time
from typing import Optional
import numpy as np
from pydub import AudioSegment

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set API keys from environment variables
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
logger.info(f"Google Credentials Path: {GOOGLE_CREDENTIALS}")

if not os.path.exists(GOOGLE_CREDENTIALS):
    logger.error(f"Google credentials file not found at: {GOOGLE_CREDENTIALS}")

def get_translate_client():
    """Get or create Google Translate client."""
    try:
        client = translate.Client()
        logger.info("Google Translate client created successfully")
        return client
    except Exception as e:
        logger.error(f"Error creating Google Translate client: {str(e)}")
        raise

def process_audio_for_recognition(audio_path: str) -> str:
    """Process audio file to improve speech recognition quality."""
    try:
        # Load audio file
        audio = AudioSegment.from_wav(audio_path)
        
        # Convert to mono if stereo
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # Normalize audio (adjust volume to optimal level)
        normalized_audio = audio.normalize()
        
        # Export processed audio to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            normalized_audio.export(temp_file.name, format='wav')
            return temp_file.name
            
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return audio_path  # Return original file if processing fails

def transcribe_audio(audio_path):
    """Transcribe audio file to text."""
    logger.info("Starting audio transcription")
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_path) as source:
            logger.info("Audio processed for recognition")
            # Adjust the recognizer sensitivity
            recognizer.dynamic_energy_threshold = True
            recognizer.energy_threshold = 300  # Lower threshold for quieter audio
            
            logger.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Get the duration of the audio file
            duration = source.DURATION
            logger.info(f"Audio duration: {duration} seconds")
            
            # Process audio in chunks of 30 seconds
            chunk_duration = 30
            offset = 0
            transcript = []
            
            while offset < duration:
                logger.info(f"Processing chunk at offset {offset} seconds")
                # Record chunk
                audio = recognizer.record(source, duration=min(chunk_duration, duration - offset))
                try:
                    # Try with English first
                    chunk_text = recognizer.recognize_google(audio, language='en-US')
                    if chunk_text.strip():
                        transcript.append(chunk_text)
                except sr.UnknownValueError:
                    logger.warning(f"Could not understand audio in chunk at offset {offset}")
                    # Skip silences
                    pass
                except sr.RequestError as e:
                    if "Bad Request" in str(e):
                        # Try without language specification
                        try:
                            chunk_text = recognizer.recognize_google(audio)
                            if chunk_text.strip():
                                transcript.append(chunk_text)
                        except (sr.UnknownValueError, sr.RequestError) as e2:
                            logger.warning(f"Second attempt failed for chunk at offset {offset}: {str(e2)}")
                            pass
                    else:
                        raise
                
                offset += chunk_duration
            
            if not transcript:
                logger.warning("No speech detected in any chunk")
                return "[Background music or minimal speech detected]"
            
            final_transcript = " ".join(transcript)
            logger.info(f"Transcription completed, length: {len(final_transcript)} characters")
            return final_transcript
            
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}", exc_info=True)
        if "malformed" in str(e).lower() or "damaged" in str(e).lower():
            raise ValueError("The audio file appears to be corrupted or in an unsupported format.")
        raise

def translate_text(text: str, target_language: str) -> str:
    """Translate text to target language using Google Translate API."""
    try:
        # Initialize the translation client
        translate_client = translate.Client()
        
        # Translate the text
        result = translate_client.translate(
            text,
            target_language=target_language
        )
        
        translated_text = result['translatedText']
        logger.info(f"Text translated to {target_language}")
        return translated_text
        
    except Exception as e:
        logger.error(f"Error in translation: {str(e)}")
        raise

def split_text(text, max_bytes=4500):
    """Split text into chunks that are within the byte limit."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        # Add 1 for the space between words
        word_size = len(word.encode('utf-8')) + 1
        if current_size + word_size > max_bytes:
            # Join current chunk and add to chunks
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            # Start new chunk
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def generate_speech(text: str, language_code: str) -> str:
    """Generate speech from text using Google Text-to-Speech."""
    try:
        # Initialize the Text-to-Speech client
        client = texttospeech.TextToSpeechClient()
        
        # Split text into chunks
        text_chunks = split_text(text)
        logger.info(f"Split text into {len(text_chunks)} chunks")
        
        # Process each chunk and collect audio data
        audio_segments = []
        
        for i, chunk in enumerate(text_chunks, 1):
            logger.info(f"Processing chunk {i}/{len(text_chunks)}")
            
            # Set the text input
            synthesis_input = texttospeech.SynthesisInput(text=chunk)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Select the audio file type
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                speaking_rate=1.0,
                pitch=0.0,
                volume_gain_db=0.0
            )
            
            # Perform the text-to-speech request
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save chunk to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(response.audio_content)
                audio_segments.append(temp_file.name)
        
        # Combine all audio segments
        if len(audio_segments) == 1:
            final_audio_path = audio_segments[0]
        else:
            # Combine audio segments using pydub
            logger.info("Combining audio segments...")
            combined = AudioSegment.from_wav(audio_segments[0])
            for segment_path in audio_segments[1:]:
                segment = AudioSegment.from_wav(segment_path)
                combined += segment
            
            # Export final audio
            final_audio_path = tempfile.mktemp(suffix='.wav')
            combined.export(final_audio_path, format='wav')
            
            # Clean up temporary files
            for segment_path in audio_segments:
                try:
                    os.remove(segment_path)
                except Exception as e:
                    logger.warning(f"Error cleaning up temporary file {segment_path}: {str(e)}")
        
        logger.info("Speech generation completed successfully")
        return final_audio_path
            
    except Exception as e:
        logger.error(f"Error in speech generation: {str(e)}")
        raise 