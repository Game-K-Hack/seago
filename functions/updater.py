import requests
import os
import gzip
import tarfile
import subprocess
import re

URL = "https://github.com/bitnami-labs/sealed-secrets/releases/latest"
TOOLS_DIR = "./tools"

def get_current_version() -> bool | str:
    realpath = os.path.realpath(TOOLS_DIR)
    exe_path = [os.path.join(realpath, filename) for filename in os.listdir(realpath) if re.match("kubeseal\\.exe", filename)][0]
    if len(exe_path) > 0:
        out = subprocess.Popen([exe_path[0], '--version'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if out.stderr.read() == b"":
            regex = re.findall(": [0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}", out.stdout.read().decode("utf8"))
            if len(regex) > 0:
                return regex[0][2:]
    return False

def new_version_available() -> bool | str:
    redirect = requests.get(URL, allow_redirects=True)
    if redirect.url != URL and get_current_version() != redirect.url.split("/")[-1][1:]:
        return redirect.url.split("/")[-1][1:]
    return False

def download_latest() -> None:
    latest_version = new_version_available()
    if latest_version:
        gz = requests.get(f"https://github.com/bitnami-labs/sealed-secrets/releases/download/v{latest_version}/kubeseal-{latest_version}-windows-amd64.tar.gz").content
        if not os.path.exists(TOOLS_DIR):
            os.makedirs(TOOLS_DIR)
        open(TOOLS_DIR + "/temp.tar", "wb").write(gzip.decompress(gz))
        tarfile.open(TOOLS_DIR + "/temp.tar").extractall(path=TOOLS_DIR)
        try: os.remove(TOOLS_DIR + "/temp.tar")
        except: pass
