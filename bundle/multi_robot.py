# import os
import subprocess
import webbrowser
# from urllib.request import pathname2url
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from bundle.resource.serve.multi_robot.web import run


def open_web():
    webpath = 'http://127.0.0.1:10025/index_old.html'
    print(webpath)
    webbrowser.open(webpath, new=2, autoraise=True)


def open_hephaestus():
    run_command(
        'java -cp hephaestus-rpc.jar com.geekplus.hephaestus.rpc.SimulatorServer')


def run_command(command):
    subprocess.Popen(command, shell=True)


def startServer(port):
    server = ThreadingHTTPServer(('', port), SimpleHTTPRequestHandler)

    print("Start server at port", port)
    server.serve_forever()


def start(port):
    thread = Thread(target=startServer, args=[port])
    thread.start()


def main():
    open_hephaestus()
    start(10025)
    open_web()
    run()


if __name__ == '__main__':
    main()
