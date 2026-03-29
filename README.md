# Flask 3D Artifact Upload & Reconstruction Service

This Flask application exposes APIs to:

- Store 3D artifact metadata in a MySQL table (`3dartifacts`).
- Upload image sets for each artifact.
- Run COLMAP CLI offline (via a batch script) to reconstruct 3D models.
- Query artifacts and optionally check whether a COLMAP model exists for them.

The metadata model is aligned with tDAR 3D sensory data objects:
https://www.tdar.org/using-tdar/creating-and-editing-resources/3d-sensory-data-objects-create-and-edit/

## Setup

1. Ensure you have Python installed.
2. Create and activate a virtual environment.
3. Install dependencies:

	 ```bash
	 pip install -r requirements.txt
	 ```

4. Configure `config.cfg` with your MySQL and COLMAP settings.
5. Run the Flask app:

	 ```bash
	 python app.py
	 ```

## Database: 3dartifacts

The table schema is defined in `create_3dartifacts.sql` and includes at least:

- `ArtifactID` (CHAR(36), primary key, UUID)
- `ProjectID`, `SiteID`, `LocationID`, `CoverageDate`
- `InvestigationTypes`, `MaterialTypes`, `CulturalTerms`, `Keywords`
- `CreatedTime` (DATETIME)
- `UploadedPics` (BOOLEAN)
- `3dModelCreatedStatus` (VARCHAR)
- `3dModelFilePath` (TEXT)
- `LogFilePath` (TEXT)

To create the table:

```bash
mysql -u <user> -p <database_name> < create_3dartifacts.sql
```

## API Endpoints

### 1) `/add_artifact` (POST, JSON)

Create a new artifact metadata record and return its `ArtifactID`.

Request body (JSON):

```json
{
	"ProjectID": "P001",
	"SiteID": "S001",
	"LocationID": "L001",
	"CoverageDate": "2025-01-15",
	"InvestigationTypes": "survey, excavation",
	"MaterialTypes": "ceramic, stone",
	"CulturalTerms": "Neolithic",
	"Keywords": "test, sample, 3d"
}
```

Response on success:

```json
{
	"ArtifactID": "<generated-uuid>"
}
```

`CreatedTime` is automatically set to the current system time.

### 2) `/upload` (POST, multipart/form-data)

Upload images for a given artifact. The server stores files under a folder named by the `ArtifactID` (from `/add_artifact`).

Form fields:

- `folder_name`: the artifact `ArtifactID` to use as the folder name.
- `image`: the image file to upload.
- `completed`: `'true'` for the last image in the set, otherwise `'false'`.

Behavior:

- Images are stored in `<cwd>/<folder_name>/pics/`.
- When `completed=true`, the server sets `UploadedPics = 1` on the matching row in `3dartifacts` and returns a message indicating that 3D model generation will be done later by a batch job.

Example final-upload response:

```json
{
	"message": "Completed pictures uploads successfully, the 3D model will be generated on the server soon. Please check on the artifact list screen on the 3D model status."
}
```

For intermediate uploads (`completed=false`), a simple success message is returned.

### 3) `/query_artifacts` (POST, JSON + optional multipart)

Query artifacts and optionally attach an image to check whether a COLMAP model exists for each artifact.

Request:

- JSON body:

	```json
	{
		"sqlwhere": "ProjectID = 'P001'"
	}
	```

	- If `sqlwhere` is omitted or empty, it defaults to `1=1`.

- Optional multipart part:
	- `picture`: image file. If provided, the server saves it to a temp folder and, for each artifact, reports whether a COLMAP model folder exists. (Actual image-vs-model matching is left for a custom implementation.)

#### cURL examples

- JSON only (no picture):

	```bash
	curl -X POST \
			 -H "Content-Type: application/json" \
			 -d '{"sqlwhere": "ProjectID = 'P001'"}' \
			 http://localhost:5000/query_artifacts
	```

- With picture (multipart form-data: sqlwhere + picture):

	```bash
	curl -X POST \
			 -F "sqlwhere=ProjectID = 'P001'" \
			 -F "picture=@/path/to/image.jpg" \
			 http://localhost:5000/query_artifacts
	```

Responses:

- Without `picture`:

	```json
	{
		"artifacts": [
			{
				"ArtifactID": "...",
				"ProjectID": "...",
				"SiteID": "...",
				"LocationID": "...",
				"CoverageDate": "...",
				"3dModelCreatedStatus": "SUCCESS",
				"3dModelFilePath": ".../sparse",
				"LogFilePath": ".../colmap_log.txt"
			}
		]
	}
	```

- With `picture`:

	```json
	{
		"artifacts": [
			{
				"ArtifactID": "...",
				"ProjectID": "...",
				"SiteID": "...",
				"LocationID": "...",
				"CoverageDate": "...",
				"3dModelCreatedStatus": "SUCCESS",
				"3dModelFilePath": ".../sparse",
				"LogFilePath": ".../colmap_log.txt",
				"match": false,
				"matchDetail": "Model folder exists; implement COLMAP-based comparison as needed."
			}
		]
	}
	```

### 4) `/download_model` (GET)

Download the reconstructed 3D model (PLY format) for a given artifact.

Query parameters:

- `uid`: the `ArtifactID` whose model to download.

The server looks for `colmap/<uid>/fused.ply` and returns it as a file download. Returns a 404 JSON error if the file is not found.

#### cURL example

```bash
curl -OJ "http://localhost:5000/download_model?uid=7b4b2b5e-6c5a-4f69-8b40-0a5c2b6f41f1"
```

Response: the `fused.ply` file is returned as an attachment download.

## Batch 3D Model Generation

3D reconstruction is handled by an offline batch script rather than inside the upload API.

- Script: `batch_generate_models.py`
- Logic:
	- Queries `3dartifacts` for rows with `UploadedPics = 1` and `3dModelCreatedStatus IS NULL`.
	- For each artifact, runs the COLMAP CLI (using paths from `config.cfg`) with the artifact folder as the workspace and `pics` as the image path.
	- Updates:
		- `3dModelCreatedStatus` to `SUCCESS` or `FAILED`.
		- `3dModelFilePath` to the reconstructed model folder (e.g. the `sparse` directory).
		- `LogFilePath` to the COLMAP log file.

Run manually (or schedule via cron / Task Scheduler):

```bash
python batch_generate_models.py
```

## Client Script

The Python client `client.py` demonstrates a typical flow:

1. Call `/add_artifact` to create metadata and obtain an `ArtifactID`.
2. Use that `ArtifactID` as `folder_name` when posting images to `/upload`.
3. Mark the final image with `completed=true` so the server sets `UploadedPics = 1`.
4. Run `batch_generate_models.py` to create the 3D model.

You can adapt `client.py` to your own image source and metadata.

## Troubleshooting

- Ensure the COLMAP CLI path in `config.cfg` exists and is executable.
- Check that the working folder has write permissions.
- If 3D model creation fails, inspect the log file path stored in `LogFilePath`.
