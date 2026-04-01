import uuid
import mysql.connector
from flask import Flask, request, jsonify, send_file
import os
import subprocess
import configparser
from flask_cors import CORS 
from datetime import datetime
from werkzeug.utils import secure_filename

config = configparser.ConfigParser()
config.read('config.cfg')

def get_db_connection():
    return mysql.connector.connect(
        host=config.get('mysql', 'host', fallback='localhost'),
        user=config.get('mysql', 'user', fallback='root'),
        password=config.get('mysql', 'password', fallback=''),
        database=config.get('mysql', 'database', fallback='3dserver')
    )

cli_path = config.get('colmap', 'cli_path', fallback='colmap.exe')
cli_args = ['automatic_reconstructor']
app = Flask(__name__)
CORS(app)  # <-- enable CORS for all routes (dev only is fine)

# New API endpoint to insert 3D artifact metadata
@app.route('/add_artifact', methods=['POST'])
def add_artifact():
    try:
        data = request.get_json(force=True)
        required_fields = [
            'ProjectID', 'SiteID', 'LocationID', 'CoverageDate',
            'InvestigationTypes', 'MaterialTypes', 'CulturalTerms', 'Keywords'
        ]
        #print("Received data for /add_artifact:", data)
        for field in required_fields:   
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        artifact_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO 3dartifacts (
                ArtifactID, ProjectID, SiteID, LocationID, CoverageDate,
                InvestigationTypes, MaterialTypes, CulturalTerms, Keywords,
                CreatedTime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                artifact_id,
                data['ProjectID'],
                data['SiteID'],
                data['LocationID'],
                data['CoverageDate'],
                data['InvestigationTypes'],
                data['MaterialTypes'],
                data['CulturalTerms'],
                data['Keywords'],
                datetime.now()
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'ArtifactID': artifact_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/query_artifacts', methods=['POST'])
def query_artifacts():
    """Query 3dartifacts with a where-clause and optionally compare a picture
    against each artifact's COLMAP workspace.

    Parameters (form-data):
    - sqlwhere: string; SQL condition for WHERE on 3dartifacts. If empty, defaults to '1=1'.
    - picture: file; optional image to compare with each artifact's COLMAP model.
    """
    # Get parameters
    # Prefer JSON payload, fall back to form field for backward compatibility.
    json_data = request.get_json(silent=True) or {}
    sqlwhere = (json_data.get('sqlwhere') or '').strip()
    if not sqlwhere:
        sqlwhere = (request.form.get('sqlwhere') or '').strip()
    if not sqlwhere:
        sqlwhere = '1=1'
    print(sqlwhere)

    picture_file = request.files.get('picture')

    # Build and execute query (caller is responsible for safe sqlwhere usage)
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT ArtifactID, ProjectID, SiteID, LocationID, CoverageDate, 3dModelCreatedStatus, 3dModelFilePath, LogFilePath FROM 3dartifacts WHERE {sqlwhere}"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({'error': f'Failed to query artifacts: {str(e)}'}), 500

    # If no picture is provided, just return the list of artifacts
    if not picture_file or picture_file.filename == '':
        return jsonify({'artifacts': rows})

    # Save the uploaded picture to a temporary location
    base_dir = os.getcwd()
    base_dir = os.path.join(base_dir, 'colmap')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    temp_dir = os.path.join(base_dir, 'query_temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    picture_filename = secure_filename(picture_file.filename)
    picture_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{picture_filename}")
    picture_file.save(picture_path)

    # Loop through artifacts and (stub) compare picture against each
    results = []
    for row in rows:
        artifact_id = row.get('ArtifactID')
        artifact_folder = os.path.join(base_dir, artifact_id)
        model_folder = os.path.join(artifact_folder, 'sparse')  # default COLMAP output for automatic_reconstructor

        # Check if a reconstructed model seems to exist
        model_exists = os.path.isdir(model_folder)

        # NOTE: Actual image-vs-model comparison using COLMAP is non-trivial
        # and depends on your pipeline (database file, camera params, etc.).
        # Here we only report whether a model folder exists; you can extend
        # this to run a custom COLMAP-based matching script.
        match_result = False
        match_detail = 'Model folder not found; no comparison performed.'
        if model_exists:
            match_detail = 'Model folder exists; implement COLMAP-based comparison as needed.'

        result_entry = {
            'ArtifactID': artifact_id,
            'ProjectID': row.get('ProjectID'),
            'SiteID': row.get('SiteID'),
            'LocationID': row.get('LocationID'),
            'CoverageDate': row.get('CoverageDate'),
            '3dModelCreatedStatus': row.get('3dModelCreatedStatus'),
            '3dModelFilePath': row.get('3dModelFilePath'),
            'LogFilePath': row.get('LogFilePath'),
            'match': match_result,
            'matchDetail': match_detail
        }
        results.append(result_entry)

    return jsonify({'artifacts': results})

@app.route('/upload', methods=['POST'])
def upload():
    folder_name = request.form.get('folder_name')
    completed = request.form.get('completed', 'false').lower() == 'true'
    file = request.files.get('image')

    if not folder_name or not file:
        return jsonify({'error': 'Missing parameters: folder_name and image are required'}), 400

    base_dir = os.getcwd()    # get current working directory
    base_dir = os.path.join(base_dir, 'colmap')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    folder_path = os.path.join(base_dir, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    pics_path = os.path.join(folder_path, 'pics')
    if not os.path.exists(pics_path):
        os.makedirs(pics_path)

    file_path = os.path.join(pics_path, file.filename)
    file.save(file_path)

    # If this is the final image, mark UploadedPics in DB and return a
    # message indicating that 3D model generation will be handled by a
    # separate batch job.
    if completed:
        try:
            conn = get_db_connection()

            cursor = conn.cursor()
            cursor.execute(
                "UPDATE 3dartifacts SET UploadedPics = 1 WHERE ArtifactID = %s",
                (folder_name,)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            return jsonify({'error': f'Failed to update UploadedPics flag: {str(e)}'}), 500

        return jsonify({
            'message': 'Completed pictures uploads successfully, the 3D model will be generated on the server soon. Please check on the artifact list screen on the 3D model status.'
        })

    # For intermediate uploads, keep a simple success message.
    return jsonify({'message': 'Image uploaded successfully', 'Started Reconstruction 3D': False})

@app.route('/download_model', methods=['GET'])
def download_model():
    uid = request.args.get('uid', '').strip()
    if not uid:
        return jsonify({'error': 'Missing parameter: uid'}), 400

    base_dir = os.path.join(os.getcwd(), 'colmap',uid, 'dense','0')  
    ply_path = os.path.join(base_dir, 'fused.ply')

    if not os.path.isfile(ply_path):
        return jsonify({'error': f'PLY file not found for uid: {uid}'}), 404

    return send_file(ply_path, mimetype='application/x-ply', as_attachment=True, download_name='fused.ply')

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5888,debug=True)
