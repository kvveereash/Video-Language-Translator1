import speech_recognition as sr
import wave
import struct
import math

def create_test_audio():
    """Create a test WAV file with a simple tone."""
    print("Creating test audio file...")
    
    # Audio parameters
    duration = 3  # seconds
    sample_rate = 44100  # Hz
    frequency = 440  # Hz (A4 note)
    
    # Create audio data
    samples = []
    for i in range(int(duration * sample_rate)):
        sample = math.sin(2 * math.pi * frequency * i / sample_rate)
        # Convert to 16-bit integer
        samples.append(int(sample * 32767))
    
    # Create WAV file
    with wave.open('test_audio.wav', 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        # Write audio data
        for sample in samples:
            wav_file.writeframes(struct.pack('h', sample))
    
    print("Test audio file created successfully!")

def test_file_recognition():
    """Test speech recognition with a file."""
    print("\nTesting file-based speech recognition...")
    
    try:
        # Create a recognizer instance
        r = sr.Recognizer()
        
        # Open the audio file
        with sr.AudioFile('test_audio.wav') as source:
            # Record the audio file
            audio = r.record(source)
            
            # Try to recognize the speech
            try:
                text = r.recognize_google(audio)
                print("Recognition successful!")
                print(f"Recognized text: {text}")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    print("=== Speech Recognition Test ===")
    create_test_audio()
    test_file_recognition() 