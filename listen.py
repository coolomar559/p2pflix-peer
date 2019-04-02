from pathlib import Path
import pickle
import socketserver
import threading

import constants
from get_configs import get_configs
from get_tracker_list import get_local_tracker_list
import ka_seq
import requests


# Class for handling requests from peers, checks for the existance of a chunk and uploads
# it to the requesting peer if it exists. Sends -1 to the peer on failure
class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        request = pickle.loads(data)

        # Construct the full file path
        full_hash = request["full_hash"]
        chunk_id = request["chunk_id"]
        file_name = f"{full_hash}#{chunk_id}"
        file_tail = Path(full_hash) / file_name
        chunk_dir = constants.CHUNK_DIRECTORY
        full_file_path = Path(chunk_dir) / file_tail

        # Check if the file exists
        if full_file_path.is_file():
            try:
                # First, send the size of the chunk
                file_size = full_file_path.stat().st_size
                self.request.sendall(pickle.dumps(file_size))

                # Then send the chunk
                with open(full_file_path, "rb") as fd:
                    self.request.sendall(fd.read())
                    return
            except EnvironmentError:
                pass

        # Send -1 file size on failure
        self.request.sendall(pickle.dumps(-1))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


# A thread class to be used for seeding files. Handles starting up a threaded TCP server
# and sending keep alive messages to the tracker
class SeedThread(threading.Thread):
    # Initialize the thread with the appropriate callback functions. Listening callback is
    # called when server is successfully listening, error callback will be called with a
    # string containing an error message on error, and shutdown callback will be called
    # when the seeder thread is shutting down.
    def __init__(self, listening_callback, error_callback, shutdown_callback):
        self.listening_callback = listening_callback
        self.error_callback = error_callback
        self.shutdown_callback = shutdown_callback
        self.stopped_event = threading.Event()
        super().__init__()

    # Stop the thread
    def stop(self):
        self.stopped_event.set()

    # Run the thread, starts the listening server and loops sending keepalives to the tracker
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

        if "guid" not in config:
            self.error_callback("Peer does not have GUID")
            self.stop()

        while not self.stopped_event.is_set():
            self.stopped_event.wait(constants.KEEPALIVE_TIME)
            data = {
                "guid": config["guid"],
                "ka_seq_number": ka_seq.get_ka_seq(),
            }
            result = self._send_keepalive(data)

            if not result["success"]:
                self.error_callback(result["error"])
                self.stop()
                continue

            ka_seq.increment_ka_seq()

        server.shutdown()
        self.shutdown_callback()

    # Try to send a keep alive to one of the trackers on the tracker list
    # Returns a JSON object of the result of the request
    def _send_keepalive(self, data):
        tracker_ips = get_local_tracker_list()
        for tracker_ip in tracker_ips:
            try:
                r = requests.put(
                    f'http://{tracker_ip}:{constants.TRACKER_PORT}/keep_alive',
                    json=data,
                    timeout=constants.REQUEST_TIMEOUT,
                )
                r.raise_for_status()
                return r.json()
            except (requests.HTTPError, requests.ConnectionError, requests.Timeout, ValueError):
                continue

        return {
            "success": False,
            "error": "No trackers available",
        }
