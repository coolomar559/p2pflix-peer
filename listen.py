from os import getcwd
from os.path import getsize, isfile, join
import pickle
import socketserver
import threading

import constants
from get_configs import get_configs
from get_tracker_list import get_local_tracker_list
import ka_seq
import requests


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        request = pickle.loads(data)

        full_hash = request["full_hash"]
        chunk_id = request["chunk_id"]
        file_name = f"{full_hash}#{chunk_id}"
        file_tail = join(full_hash, file_name)

        # TODO: THIS NEEDS TO COME FROM A CONFIG FILE
        files_directory = getcwd() + "/files/"

        full_path = join(files_directory, file_tail)
        if isfile(full_path):
            try:
                # First, send the size of the chunk
                file_size = getsize(full_path)
                self.request.sendall(pickle.dumps(file_size))
                print("sent file size")

                # Then send the chunk
                f = open(full_path, "rb")
                self.request.sendall(f.read())
                print("sent file")
                return
            except EnvironmentError:
                print("Could not access file")
        else:
            print(f"Could not find file {full_path}")

        self.request.sendall(pickle.dumps(-1))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class SeedThread(threading.Thread):
    def __init__(self, listening_callback, error_callback, shutdown_callback):
        self.listening_callback = listening_callback
        self.error_callback = error_callback
        self.shutdown_callback = shutdown_callback
        self.stopped_event = threading.Event()
        super().__init__()

    def stop(self):
        self.stopped_event.set()

    def run(self):
        ip = constants.LISTEN_IP
        port = constants.PEER_PORT

        server = ThreadedTCPServer((ip, port), RequestHandler)

        t = threading.Thread(target=server.serve_forever)
        t.daemon = True
        t.start()
        self.listening_callback()

        config = get_configs()
        if "success" in config and not config["success"]:
            self.error_callback(config["error"])
            self.stop()

        while not self.stopped_event.isSet:
            self.stopped_event.wait(constants.KEEPALIVE_TIME)
            data = {
                "guid": config["guid"],
                "ka_seq_number": ka_seq.get_ka_seq(),
            }
            tracker_ips = get_local_tracker_list()
            for tracker_ip in tracker_ips:
                try:
                    requests.put(f'http://:{constants.TRACKER_PORT}/keep_alive', json=data)
                    r.raise_for_status()
                    return r.json()
                except (requests.HTTPError, requests.ConnectionError, requests.Timeout, ValueError) as e:
                    return {
                        "success": False,
                        "error": str(e),
                    }

        self.shutdown_callback()
        server.shutdown()
