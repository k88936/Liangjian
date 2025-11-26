from threading import Thread
import webbrowser
# import os
import subprocess
# from urllib.request import pathname2url
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from bundle.resource.serve.multi_robot.cli import go


def open_web():
    webpath = 'http://127.0.0.1:10025/index_old.html'
    webbrowser.open(webpath, new=2, autoraise=True)

import glob
import zipfile
import os


def open_hephaestus():
    run_command(
        'java -cp hephaestus-rpc.jar com.geekplus.hephaestus.rpc.SimulatorServer')


def run_command(command):
    subprocess.Popen(command, shell=True)

def main():
    open_hephaestus()
    go(replay=False,record=True)


if __name__ == '__main__':
    main()
    with zipfile.ZipFile("~/Downloads/k88936的团队.zip", "w") as zf:
        for path in glob.glob("../result_*.json"):
            zf.write(path, arcname=os.path.join("results", os.path.basename(path)))
