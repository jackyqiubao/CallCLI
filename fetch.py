# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "aspose-3d",
#     "requests>=2.31.0",
#     "alive-progress==3.3.0",
#     "about-time==4.2.1",
#     "graphemeu==0.7.2"
# ]
# ///
import requests, os, time, glob, uuid           
import aspose.threed as a3d
from pathlib import Path
from alive_progress import alive_bar

scan_name= uuid.uuid4()
scanner_ip = '192.168.29.193'

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

def download_all(count=80, scanner_ip='192.168.29.193'):
    print('Downloading Images:')
    with alive_bar(count) as bar:
        for i in range(count):
            download_file(f'http://{scanner_ip}:1234/images/captured_img{i}.png', f'processing{i}.png')
            bar()

def start_scan(scanner_ip='192.168.29.193', count=80):
    try:
        get((f'http://{scanner_ip}:1234/scancustom/1/{count}'), timeout=1)
    except Exception as e:
        pass
    print('Starting Scan')
    count = 156
    with alive_bar(count) as bar:
        for i in range(count):
            time.sleep(1)
            bar()
    return

def stop_scan(scanner_ip='192.168.29.193'):
    try:
        get((f'http://{scanner_ip}:1234/stop/'), timeout=1)
    except Exception as e:
        pass

if __name__ == '__main__':
    download_all()
