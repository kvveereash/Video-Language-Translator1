from flask import request, jsonify, send_file
from app import app, celery
from app.tasks import process_video, process_youtube_video
import os

@app.route('/api/translate', methods=['POST'])
def translate_video():
    target_language = request.form.get('target_language', 'en')
    
    if 'video' in request.files:
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Save the video file temporarily
        video_path = os.path.join('uploads', video_file.filename)
        os.makedirs('uploads', exist_ok=True)
        video_file.save(video_path)
        
        # Process video asynchronously
        task = process_video.delay(video_path, target_language)
        
    elif 'youtube_url' in request.form:
        youtube_url = request.form.get('youtube_url')
        if not youtube_url:
            return jsonify({'error': 'No YouTube URL provided'}), 400
        
        # Process YouTube video asynchronously
        task = process_youtube_video.delay(youtube_url, target_language)
        
    else:
        return jsonify({'error': 'No video file or YouTube URL provided'}), 400

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
    video_path = os.path.join('outputs', f'{video_id}.mp4')
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video not found'}), 404
    return send_file(video_path, as_attachment=True) 