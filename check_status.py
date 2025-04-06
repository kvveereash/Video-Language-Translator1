import requests
import time

task_id = "c269947d-93b1-4923-80fd-7c9990fbd64b"  # Replace with your task ID
url = f'http://127.0.0.1:5000/api/status/{task_id}'

# Check status every 5 seconds
while True:
    response = requests.get(url)
    print('Status:', response.json())
    
    if response.json().get('state') == 'SUCCESS':
        break
    
    time.sleep(5) 