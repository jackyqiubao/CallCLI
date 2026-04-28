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
#     "requests>=2.31.0",
#     "urllib3>=2.6.3",
#     "werkzeug>=2.3.7",
#     "alive-progress==3.3.0",
#     "about-time==4.2.1",
#     "graphemeu==0.7.2"
# ]
# ///
import requests, os, time, glob, uuid, subprocess, fetch
from aspose.threed import Scene, FileFormat
from pathlib import Path
from alive_progress import alive_bar

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
    return subprocess.run(command, shell=True)

def photogrammetry_path():
    return os.getcwd() + '/operation'

def photogrammetry(imagepath, outputpath, outputname):
    command = os.path.join(os.getcwd(), 'operation') + ' ' + imagepath + ' ' + os.path.join(os.getcwd(), outputpath, outputname)
    print('Starting Photogrammetry Operation')
    run_command(command)

def scan(count=80, scanner_ip='192.168.29.193'):
    fetch.start_scan(scanner_ip=scanner_ip, count=count)
    fetch.download_all(scanner_ip=scanner_ip, count=count)
    photogrammetry(os.getcwd(), os.getcwd(), f'scan{uuid.uuid4()}.usdz')
    run_command('rm processing*.png')
    fetch.stop_scan(scanner_ip=scanner_ip)
    return('Scan Success!')

def process(count=80, scanner_ip='192.168.29.193'):
    fetch.download_all(scanner_ip=scanner_ip, count=count)
    photogrammetry(os.getcwd(), os.getcwd(), f'scan{uuid.uuid4()}.usdz')
    run_command('rm processing*.png')
    fetch.stop_scan(scanner_ip=scanner_ip)
    return('Scan Success!')

if __name__ == '__main__':
    print('Ancient Vision Api Shell:')
    print('v0.1 - Licensed under MIT')
    while True:
        try:
            exec(input('--> '))
        except Exception as e:
            print(e)
