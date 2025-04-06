import wave
import math
import struct

def create_test_audio():
    # Audio parameters
    duration = 5  # seconds
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
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        # Write audio data
        for sample in samples:
            wav_file.writeframes(struct.pack('h', sample))

    print("Test audio file created successfully!")

if __name__ == "__main__":
    create_test_audio() 