import os
import subprocess
import configparser
import mysql.connector
from datetime import datetime

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
        print("No pending artifacts found.")
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

        # Run COLMAP command (same as in app.py upload)
        try:
            command = [cli_path] + cli_args + ["--workspace_path", folder_path, "--image_path", pics_path]

            if os.name == 'nt':  # Windows
                env = os.environ.copy()
                # Adjust this path if needed, keep consistent with app.py
                env['QT_QPA_PLATFORM_PLUGIN_PATH'] = "D:\\QB\\code\\Colmap\\colmap_nocuda\\plugins\\platforms"
                with open(log_path, 'w') as logfile:
                    result = subprocess.run(
                        command,
                        stdout=logfile,
                        stderr=subprocess.STDOUT,
                        text=True,
                        env=env
                    )
            else:
                with open(log_path, 'w') as logfile:
                    result = subprocess.run(
                        command,
                        stdout=logfile,
                        stderr=subprocess.STDOUT,
                        text=True
                    )

            if result.returncode == 0:
                status = 'SUCCESS'
                # Point to the generated sparse model folder as a simple model path
                model_path = os.path.join(folder_path, 'sparse')
                print(f"Artifact {artifact_id} processed successfully.")
            else:
                status = 'FAILED'
                model_path = None
                print(f"Artifact {artifact_id} failed, see log at {log_path}.")

            update_status(artifact_id, status, model_path, log_path)

        except Exception as e:
            print(f"Error processing artifact {artifact_id}: {e}")
            update_status(artifact_id, 'FAILED', None, log_path, error_message=str(e))


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


if __name__ == '__main__':
    process_pending_artifacts()
