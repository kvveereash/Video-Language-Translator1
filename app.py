from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Celery
app.config['CELERY_broker_url'] = os.getenv('CELERY_broker_url', 'redis://localhost:6379/0')
app.config['result_backend'] = os.getenv('result_backend', 'redis://localhost:6379/0')

celery = Celery(
    app.name,
    broker=app.config['CELERY_broker_url'],
    backend=app.config['result_backend']
)
celery.conf.update(app.config)

# Import tasks after celery initialization
from app.tasks import process_video, process_youtube_video

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    target_language = request.form.get('target_language', 'en')
    
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the video file temporarily
    video_path = os.path.join('uploads', video_file.filename)
    os.makedirs('uploads', exist_ok=True)
    video_file.save(video_path)
    
    # Process video asynchronously
    task = process_video.delay(video_path, target_language)
    
    return jsonify({
        'task_id': task.id,
        'status': 'processing'
    })

@app.route('/api/youtube', methods=['POST'])
def process_youtube():
    data = request.get_json()
    youtube_url = data.get('url')
    target_language = data.get('target_language', 'en')
    
    if not youtube_url:
        return jsonify({'error': 'No YouTube URL provided'}), 400
    
    # Process YouTube video asynchronously
    task = process_youtube_video.delay(youtube_url, target_language)
    
    return jsonify({
        'task_id': task.id,
        'status': 'processing'
    })

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = celery.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is pending...'
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        response = {
            'state': task.state,
            'error': str(task.info)
        }
    
    return jsonify(response)

@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    try:
        video_path = os.path.join('outputs', f'{video_id}.mp4')
        if not os.path.exists(video_path):
            return jsonify({
                'status': 'error',
                'error': 'Video not found. The video might have failed to process or has been deleted.'
            }), 404
            
        # Check if the file is empty or corrupted
        if os.path.getsize(video_path) == 0:
            return jsonify({
                'status': 'error',
                'error': 'Video file is empty or corrupted. Please try processing the video again.'
            }), 500
            
        return send_file(
            video_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name='translated_video.mp4'
        )
        
    except Exception as e:
        app.logger.error(f"Error downloading video: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to download video. Please try again.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 