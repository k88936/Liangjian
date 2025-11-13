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
