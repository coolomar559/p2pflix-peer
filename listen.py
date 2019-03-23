# import configparser
import json
from os import getcwd
from os.path import isfile, join
import socketserver
import threading
import time

import requests


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # TODO: THIS NEEDS TO COME FROM A CONFIG FILE
        filepath = getcwd() + '/files/'

        data = str(self.request.recv(1024), 'ascii')
        request_json = json.JSONDecoder().decode(data)
        hsh = request_json["full_hash"]
        chnk = request_json["chunk_id"]
        fname = hsh + '#' + str(chnk)
        fdir = join(hsh, fname)
        absdir = join(filepath, fdir)
        print(isfile(absdir))
        if isfile(absdir):
            try:
                f = open(absdir, 'rb')
                print("Success")
                self.request.sendall(f.read())
                return
            except IOError:
                print("Failed to open")
        else:
            print("No file here")

        response = -1
        self.request.sendall(response)
        return


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def seed():
    ip = 'localhost'
    port = 65432

    server = ThreadedTCPServer((ip, port), RequestHandler)

    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()
    print("Server loop running")

# TODO: This needs to come from the config file
#    config = get_configs()
#    data['guid'] = config['guid']
    data = {'guid': 1}
    try:
        alive = True
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        while alive:
            time.sleep(60)
            requests.put('http://127.0.0.1:42069/keep_alive', json.dumps(data), headers=headers)
    except KeyboardInterrupt:
        print("Shutdown Initiated.")

    server.shutdown()
