import hashlib
import ipaddress
import json
import os
import socket
import time

import requests


def request_file_list(**kwargs):
    my_ip = str()

    for key, _value in kwargs.items():
        if key == 'ip' and ipaddress.ip_address(kwargs['ip']):
            my_ip = kwargs['ip']
    if not my_ip:
        my_ip = "localhost"
    r = requests.get('http://' + str(my_ip) + ':42069/file_list')
    r_json = r.json()
    print(json.dumps(r_json, indent=4))


def request_file_details_from_tracker(file_id, **kwargs):
    my_ip = str()
    for key, _value in kwargs.items():
        if key == 'ip' and ipaddress.ip_address(kwargs['ip']):
            print(kwargs['ip'])
            my_ip = kwargs['ip']
    if not my_ip:
        my_ip = "localhost"
    r = requests.get('http://' + str(my_ip) + ':42069/file/' + str(file_id))
    return r.text
# TODO: will probably need to add some error checking and stuff here


def request_file_from_peer(file_id):
    file_details_json = json.loads(str(request_file_details_from_tracker(file_id)))
    print(json.dumps(file_details_json, indent=4))
    if file_details_json["success"] is True:
        print("successfully got file details from tracker")
    else:
        print("failed to get file details from tracker")
        exit(0)

    chunk_counter = 0
    peer_counter = 0
    num_of_available_peers_for_file = len(file_details_json['peers'])
    if os.path.exists(file_details_json['name']):
        os.remove(file_details_json['name'])
    f = open(file_details_json['name'], 'ab')

    while chunk_counter < len(file_details_json["chunks"]):
        if peer_counter > (3 * num_of_available_peers_for_file):
            print("can't find enough working peers. please try again later")
            exit(0)
        send_file_request_json = {
            "full_hash": file_details_json["full_hash"],
            "chunk_id": file_details_json["chunks"][chunk_counter]["id"]}
        send_file_request_json = json.dumps(send_file_request_json)
        print(send_file_request_json)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((json.dumps(file_details_json["peers"]
                                  [peer_counter % len(file_details_json["peers"])]["ip"]).replace('"', ""), 65432))
        except Exception:
            peer_counter = peer_counter + 1
        s.sendall(bytes(send_file_request_json, 'ascii'))
        received_data = s.recv(1572864)
        # received_data = recvall(s, 1000000)
        actual_hash = hashlib.sha256(received_data).hexdigest()
        if (actual_hash == file_details_json["chunks"][chunk_counter]["chunk_hash"]):
            print("successfully received a chunk")
            chunk_counter = chunk_counter + 1
            f.write(received_data)
        else:
            print("actual hash: " + actual_hash)
            print("expected hash: " + file_details_json["chunks"][chunk_counter]["chunk_hash"])
            print("failed to receive a chunk")
            peer_counter = peer_counter + 1
        s.shutdown(1)
        s.close()
        time.sleep(3)
    f.close()

    block_size = 1000000
    sha256 = hashlib.sha256()
    with open(file_details_json['name'], 'rb') as f:
        buf = f.read(block_size)
        while len(buf) > 0:
            sha256.update(buf)
            buf = f.read(block_size)

    if sha256.hexdigest() == file_details_json["full_hash"]:
        print("final check sum succeeded. Your file is ready")
    else:
        print("The final check sum failed. Please try again.")


def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = b''
        try:
            packet = sock.recv()
        except socket.timeout:
            print()
        except Exception:
            print()
        print("here")
        if packet == b'':
            return data
        data += packet
    return data
