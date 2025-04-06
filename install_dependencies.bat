@echo off
echo Installing required packages...

pip install --no-cache-dir pydub
pip install --no-cache-dir gTTS
pip install --no-cache-dir SpeechRecognition
pip install --no-cache-dir ffmpeg-python

echo.
echo Installation completed!
echo You can now run test_recognition.py
pause 