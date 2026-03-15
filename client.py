import requests
import uuid
import sys
import os

'''
if len(sys.argv) != 2:
    print("Usage: python client.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]
if not os.path.exists(image_path):
    print(f"Image file does not exist: {image_path}")
    sys.exit(1)
'''
image_path ="/Users/jackyqiu/Code/PicturesTo3D/matirial/2DPictures/IMG_20260306_105456.jpg"

folder_name = str(uuid.uuid4())
print(folder_name)
with open(image_path, 'rb') as f:
    files = {'image': f}
    data = {'folder_name': folder_name, 'completed': 'false'}
    response = requests.post('http://localhost:5000/upload', files=files, data=data)

print("Response:", response.json())