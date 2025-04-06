import os
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import tempfile

def create_sample_audio():
    """Create a sample audio file using Google Text-to-Speech."""
    print("\n=== Creating Test Audio ===")
    
    # Create a text sample
    text = "Hello, this is a test of the speech recognition system."
    
    try:
        # Create temporary directory if it doesn't exist
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Paths for audio files
        mp3_path = os.path.join(temp_dir, 'test.mp3')
        wav_path = os.path.join(temp_dir, 'test.wav')
        
        print("Generating speech from text...")
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(mp3_path)
        print("Speech generated successfully!")
        
        print("Converting to WAV format...")
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format='wav')
        print("Conversion completed!")
        
        return wav_path, text
        
    except Exception as e:
        print(f"\nError creating audio: {str(e)}")
        return None, None

def test_recognition(audio_path, original_text):
    """Test speech recognition with the generated audio file."""
    print("\n=== Testing Speech Recognition ===")
    
    if not audio_path or not os.path.exists(audio_path):
        print("Error: No audio file available for testing")
        return False
    
    # Create a recognizer instance
    recognizer = sr.Recognizer()
    
    try:
        print(f"Reading audio file: {audio_path}")
        with sr.AudioFile(audio_path) as source:
            print("Processing audio...")
            audio = recognizer.record(source)
            
            print("Performing speech recognition...")
            try:
                text = recognizer.recognize_google(audio)
                print("\nRecognition Results:")
                print(f"Original text: {original_text}")
                print(f"Recognized text: {text}")
                
                # Calculate similarity
                similarity = len(set(text.lower().split()) & set(original_text.lower().split())) / len(set(original_text.lower().split()))
                print(f"Text similarity: {similarity:.1%}")
                
                return True
                
            except sr.UnknownValueError:
                print("\nError: Speech recognition could not understand the audio")
                return False
            except sr.RequestError as e:
                print(f"\nError: Could not request results from speech recognition service; {e}")
                return False
    except Exception as e:
        print(f"\nError during recognition: {str(e)}")
        return False

def cleanup():
    """Clean up temporary files."""
    try:
        if os.path.exists('temp'):
            for file in os.listdir('temp'):
                os.remove(os.path.join('temp', file))
            os.rmdir('temp')
    except Exception as e:
        print(f"Note: Could not clean up temporary files: {e}")

if __name__ == "__main__":
    print("=== Speech Recognition System Test ===")
    
    try:
        # Create test audio
        audio_path, original_text = create_sample_audio()
        
        # Test recognition
        if audio_path:
            success = test_recognition(audio_path, original_text)
            print("\n=== Test Summary ===")
            print("Speech Recognition Test:", "✓ Passed" if success else "✗ Failed")
        
        # Clean up
        cleanup()
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        cleanup()