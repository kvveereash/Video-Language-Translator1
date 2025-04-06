# Video Language Translator

A Flask-based web application that translates videos into different languages while maintaining lip synchronization using Wav2Lip technology.

## Features

- Video upload and YouTube URL support
- Multiple language translation options
- Lip-synchronized speech generation
- Real-time progress tracking
- Web-based interface

## Project Structure

```
Video-Language-Translator/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── tasks.py           # Celery tasks
│   └── utils/             # Utility modules
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS)
├── media/                # Media files
│   ├── test_videos/     # Test video files
│   └── test_audio/      # Test audio files
├── scripts/             # Setup and utility scripts
├── tests/              # Test files
├── models/             # Model files
├── Wav2Lip/           # Wav2Lip module
├── uploads/           # Uploaded video storage
├── outputs/           # Processed video storage
├── credentials/       # API credentials
└── frontend/         # Frontend assets
```

## Prerequisites

- Python 3.11.6
- Redis Server
- FFmpeg
- Google Cloud credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Video-Language-Translator.git
cd Video-Language-Translator
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Place Google Cloud credentials in:
```
credentials/google-credentials.json
```

## Running the Application

1. Start Redis server:
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A app.celery worker --loglevel=info --pool=solo
```

3. Start Flask application:
```bash
python app.py
```

4. Access the application at:
```
http://localhost:5000
```

## Development

- Use `scripts/` directory for utility scripts
- Store test files in `tests/` directory
- Keep media files in `media/` directory
- Follow PEP 8 style guide

## Testing

Run tests using:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Wav2Lip for lip synchronization
- Google Cloud for translation services
- FFmpeg for video processing 