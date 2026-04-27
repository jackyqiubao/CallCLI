import requests, os, time, glob, uuid
from aspose.threed import Scene, FileFormat
from pathlib import Path
import subprocess

scan_name = uuid.uuid4()
scanner_ip = '192.168.12.1'

def get(url, timeout=10):
    resp = requests.get(url, stream=True, timeout=timeout)
    try:
        resp.raise_for_status()
        return resp
    finally:
        resp.close()

def download_file(url, local_filename):
    local_filename = os.path.join(os.path.dirname(__file__), local_filename)
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()

            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        return local_filename
    except requests.exceptions.RequestException as e:
        return e

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

def photogrammetry(imagepath, outputname):
    command = [os.path.join(os.getcwd(), 'operation'), os.path.join(os.getcwd(), imagepath), os.path.join(os.getcwd(), imagepath, outputname)]
    run_command(command)
    scn = Scene.from_file(os.path.join(os.getcwd(), imagepath, outputname + ".usdz"))
    scn.save(os.path.join(os.getcwd(), imagepath, outputname + ".ply"))
    scn.save(os.path.join(os.getcwd(), imagepath, outputname + ".glb"))
    scn.save(os.path.join(os.getcwd(), imagepath, outputname + ".stl"))
    return[os.path.join(os.getcwd(), imagepath, outputname + ".ply"), os.path.join(os.getcwd(), imagepath, outputname + ".glb"), os.path.join(os.getcwd(), imagepath, outputname + ".stl")]
