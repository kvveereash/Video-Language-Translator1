import os
from dotenv import load_dotenv
from openai import OpenAI
from google.cloud import translate_v2 as translate
import requests

# Load environment variables
print("Loading environment variables...")
load_dotenv()

def test_openai():
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Test with a simple completion
        print("Testing OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print("OpenAI API test successful")
        return True
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        return False

def test_google_translate():
    try:
        print("Testing Google Translate API...")
        client = translate.Client()
        result = client.translate('Hello', target_language='es')
        print(f"Translation test successful: {result['translatedText']}")
        return True
    except Exception as e:
        print(f"Google Translate API Error: {str(e)}")
        return False

def test_elevenlabs():
    try:
        print("Testing ElevenLabs API...")
        # Use the API key directly
        api_key = "sk_09d186d0287918ef252892c80d13d2a55a1ea17d10f00ae2"
        print(f"Using API key: {api_key}")
        
        # Use Rachel's voice ID (a default voice)
        voice_id = "21m00Tcm4TlvDq8ikWAM"
        
        # Test text-to-speech generation
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Xi-Api-Key": api_key
        }
        
        data = {
            "text": "Hello, this is a test.",
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        }
        
        print("Sending request to ElevenLabs...")
        print(f"Request URL: {url}")
        print(f"Headers: {headers}")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            print("Successfully generated speech")
            return True
        else:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            return False
            
    except Exception as e:
        print(f"ElevenLabs API Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("\nTesting API Keys...")
    print("-" * 50)
    
    openai_result = test_openai()
    google_result = test_google_translate()
    elevenlabs_result = test_elevenlabs()
    
    print("\nResults:")
    print(f"OpenAI API: {'✅ Working' if openai_result else '❌ Not Working'}")
    print(f"Google Translate API: {'✅ Working' if google_result else '❌ Not Working'}")
    print(f"ElevenLabs API: {'✅ Working' if elevenlabs_result else '❌ Not Working'}") 