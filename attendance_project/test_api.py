# test_api.py
import requests

url = 'http://127.0.0.1:8000/api/mark-attendance/'
# Change this path to the image of yourself!
image_path = r'C:\Users\saroj\Documents\FaceRecognition Attendance\images\Saroj_1001.jpg' 

with open(image_path, 'rb') as img:
    files = {'image': img}
    response = requests.post(url, files=files)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())