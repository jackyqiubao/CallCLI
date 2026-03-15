# Flask Image Upload Interface

This Flask application provides an endpoint to upload images to a specified folder, creating the folder structure if necessary, and optionally calling a CLI tool when the upload is completed.

## Setup

1. Ensure you have Python installed.
2. Create a virtual environment and activate it.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `python app.py`

## Usage

Send a POST request to `/upload` with the following parameters:

- `folder_name`: The name of the folder to save images in.
- `image`: The image file to upload (multipart/form-data).
- `completed`: A flag ('true' or 'false') indicating if the upload is complete.

Example using curl:

```bash
curl -X POST -F "folder_name=my_project" -F "image=@path/to/image.jpg" -F "completed=false" http://localhost:5000/upload
```

When `completed=true`, the application will call the specified CLI tool with the pics folder and output path.

## Client

A Python client script is provided to test the API.

Usage: `python client.py <path_to_image_file>`

This will generate a GUID for the folder name, upload the image with `completed=false`, and print the response.

## Troubleshooting

- Ensure the CLI path exists and is executable.
- Check that the folder has write permissions.
- If the CLI fails, check the error message in the response.# CallCLI
