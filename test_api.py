import requests
import time

def test_upload():
    url = 'http://127.0.0.1:5000/api/translate'
    try:
        with open('uploads/test_with_audio.mp4', 'rb') as f:
            files = {
                'video': ('test_with_audio.mp4', f, 'video/mp4')
            }
            data = {
                'target_language': 'es'
            }
            response = requests.post(url, files=files, data=data)
            print('Response:', response.status_code)
            print('Content:', response.text)
            return response.json().get('task_id')
    except Exception as e:
        print('Error:', str(e))
        return None

def check_status(task_id):
    if not task_id:
        return
    
    url = f'http://127.0.0.1:5000/api/status/{task_id}'
    while True:
        try:
            response = requests.get(url)
            status = response.json()
            print('Status:', status)
            
            if status.get('state') == 'SUCCESS':
                break
            
            time.sleep(5)
        except Exception as e:
            print('Error checking status:', str(e))
            time.sleep(5)

if __name__ == '__main__':
    task_id = test_upload()
    if task_id:
        check_status(task_id) 