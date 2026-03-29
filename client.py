import requests

import os

# Change this path to your local image path
image_path = "D:\QB\code\Colmap\pic6"

# --- Step 1: call /add_artifact to create metadata and get UID ---
artifact_metadata = {
    "ProjectID": "P001",
    "SiteID": "S001",
    "LocationID": "L001",
    "CoverageDate": "2025-01-15",
    "InvestigationTypes": "survey, excavation",
    "MaterialTypes": "ceramic, stone",
    "CulturalTerms": "Neolithic",
    "Keywords": "test, sample, 3d"
}

artifact_response = requests.post("http://localhost:5000/add_artifact", json=artifact_metadata)

if artifact_response.status_code != 200:
    print(f"Failed to add artifact: {artifact_response.status_code} - {artifact_response.text}")
    raise SystemExit(1)

artifact_json = artifact_response.json()
artifact_id = artifact_json.get("ArtifactID")

if not artifact_id:
    print(f"add_artifact did not return ArtifactID: {artifact_json}")
    raise SystemExit(1)

print(f"Created artifact with ID: {artifact_id}")

# Use the ArtifactID as the folder name for uploads
folder_name = artifact_id

file_list = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
num_files = len(file_list)

for idx, filename in enumerate(file_list):
    file_full_path = os.path.join(image_path, filename)
    with open(file_full_path, 'rb') as f:
        files = {'image': f}
        completed = 'true' if idx == num_files - 1 else 'false'
        data = {'folder_name': folder_name, 'completed': completed}
        response = requests.post('http://localhost:5000/upload', files=files, data=data)
    print(f"Sent {filename}, completed={completed}, response: {response.json()}")