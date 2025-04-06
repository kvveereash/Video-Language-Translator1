import os
import speech_recognition as sr
from pydub import AudioSegment
import tempfile

def test_transcription():
    """Test transcription from audio file."""
    audio_path = "test_audio.wav"
    
    print("\n=== Testing File-based Transcription ===")
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return False
        
    try:
        # Initialize recognizer
        r = sr.Recognizer()
        
        # Convert wav to raw audio data
        print("Processing audio file...")
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
            
        # Try recognition
        print("Performing recognition...")
        try:
            text = r.recognize_google(audio)
            print(f"Transcription successful!")
            print(f"Transcribed text: {text}")
            return True
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return False
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return False
            
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return False

def test_recognition():
    """Test real-time speech recognition from microphone."""
    print("\n=== Testing Microphone-based Recognition ===")
    try:
        # Initialize recognizer
        r = sr.Recognizer()
        
        # Test microphone availability
        print("Checking microphone...")
        with sr.Microphone() as source:
            print("Microphone found. Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            
            print("Please speak something (5 seconds)...")
            audio = r.listen(source, timeout=5)
            
        print("Processing audio...")
        text = r.recognize_google(audio)
        print(f"You said: {text}")
        return True
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return False
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Speech Recognition Tests...")
    
    # Test file-based transcription
    file_result = test_transcription()
    print(f"\nTest Summary:")
    print(f"File-based transcription: {'✓' if file_result else '✗'}")
    
    # Test microphone-based recognition
    mic_result = test_recognition()
    print(f"Microphone-based test {'passed' if mic_result else 'failed'}")
    
    print("\nTest Summary:")
    print(f"File-based transcription: {'✓' if file_result else '✗'}")
    print(f"Microphone recognition: {'✓' if mic_result else '✗'}") 