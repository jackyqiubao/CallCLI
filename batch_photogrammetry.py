# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "aspose-3d",
#     "blinker>=1.9.0",
#     "certifi>=2026.4.22",
#     "charset-normalizer>=3.4.7",
#     "click>=8.3.3",
#     "colorama>=0.4.6",
#     "flask>=2.3.3",
#     "flask-cors>=4.0.0",
#     "idna>=3.13",
#     "itsdangerous>=2.2.0",
#     "jinja2>=3.1.6",
#     "markupsafe>=3.0.3",
#     "mysql-connector-python>=8.3.0",
#     "requests>=2.31.0",
#     "urllib3>=2.6.3",
#     "werkzeug>=2.3.7",
# ]
# ///
import os, subprocess, configparser, mysql.connector, runpy
from datetime import datetime
from aspose.threed import Scene, FileFormat
from time import sleep as wait

def run_command(command):
    result = subprocess.run(
        command, 
        shell=True, 
        executable='/bin/zsh',
        capture_output=True,
        text=True           
    )
    return result

def photogrammetry_path():
    return os.getcwd() + '/operation'

def photogrammetry(imagepath, outputpath, outputname):
    command = [os.path.join(os.getcwd(), 'operation'), imagepath, os.path.join(os.getcwd(), outputpath, outputname)]
    print(command)
    run_command(command)
    try:
        scn = Scene.from_file(os.path.join(os.getcwd(), outputpath, outputname + ".usdz"))
        scn.save(os.path.join(os.getcwd(), outputpath, outputname + ".ply"))
        scn.save(os.path.join(os.getcwd(), outputpath, outputname + ".glb"))
        scn.save(os.path.join(os.getcwd(), outputpath, outputname + ".stl"))
        return[os.path.join(os.getcwd(), outputpath, outputname + ".ply"), os.path.join(os.getcwd(), outputpath, outputname + ".glb"), os.path.join(os.getcwd(), outputpath, outputname + ".stl")]
    except Exception as e:
        print(f"Error occurred while processing {outputname}: {e}")
        return None

# Load configuration (reuse config.cfg like app.py)
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


def process_pending_artifacts():
    """Query artifacts with UploadedPics = 1 and 3dModelCreatedStatus IS NULL,
    then run COLMAP for each and update status/log/model path.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT ArtifactID
        FROM 3dartifacts
        WHERE UploadedPics = 1 AND 3dModelCreatedStatus IS NULL
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        print("No pending artifacts found.", datetime.now())
        return

    base_dir = os.getcwd()
    base_dir = os.path.join(base_dir, 'colmap')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    for row in rows:
        artifact_id = row['ArtifactID']
        print(f"Processing artifact {artifact_id}...")

        folder_path = os.path.join(base_dir, artifact_id)
        pics_path = os.path.join(folder_path, 'pics')
        log_path = os.path.join(folder_path, 'colmap_log.txt')

        # Ensure paths exist
        if not os.path.isdir(pics_path):
            print(f"Pics path not found for artifact {artifact_id}: {pics_path}")
            update_status(artifact_id, 'FAILED', None, log_path, error_message='Pics path not found')
            continue
            
        photogrammetry(folder_path, pics_path, 'sparse.usdz')


        status = 'SUCCESS'
        # Point to the generated sparse model folder as a simple model path
        model_path = os.path.join(folder_path, 'sparse')
        print(f"Artifact {artifact_id} processed successfully.")

        update_status(artifact_id, status, model_path, log_path)



def update_status(artifact_id, status, model_path, log_path, error_message=None):
    """Update 3dModelCreatedStatus, 3dModelFilePath, and LogFilePath in the DB."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE 3dartifacts
            SET 3dModelCreatedStatus = %s,
                3dModelFilePath = %s,
                LogFilePath = %s
            WHERE ArtifactID = %s
            """,
            (status, model_path, log_path, artifact_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Failed to update status for artifact {artifact_id}: {e}")


while True:
    process_pending_artifacts()
    wait(2)
