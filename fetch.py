import requests, os, time, glob, uuid           
import aspose.threed as a3d
from pathlib import Path

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


for i in range(80):
    download_file(f'http://{scanner_ip}:1234/images/captured_img{i}.png', f'processing{i}.png')
    print('Downloaded image', i)
