from concurrent import futures
import hashlib
# import ipaddress
import json
import os
import socket

from get_tracker_list import get_t_list
import requests


T_PORT = 42069


def request_file_list():
    tracker_ips = get_t_list()
    for tracker_ip in tracker_ips:
        try:
            r = requests.get('http://' + str(tracker_ip) + ':' + str(T_PORT) + '/file_list')
        except Exception:
            continue
        r_json = r.json()
        print(json.dumps(r_json, indent=4))
        return r_json


def request_file_details_from_tracker(file_hash):
    tracker_ips = get_t_list()
    for tracker_ip in tracker_ips:
        try:
            r = requests.get('http://' + str(tracker_ip) + ':' + str(T_PORT) + '/file_by_hash/' + file_hash)
            file_details_json = json.loads(r.text)
            if file_details_json['success']:
                return file_details_json
            else:
                continue
        except Exception:
            continue
    return None
# TODO: will probably need to add some error checking and stuff here


def get_full_file(full_file_hash, num_of_threads=6):
    file_details_json = request_file_details_from_tracker(full_file_hash)
    if file_details_json is None:
        print("Could not find a file with this hash at any known trackers.")
        print("Please try a different hash or different trackers")
        return
    if not download_many(file_details_json, num_of_threads):
        print("Failed to download. Please try again later.")
    # combine_chunks(file_details_json)


def download_many(file_details_json, num_of_threads):
    workers = min(num_of_threads, len(file_details_json['chunks']))
    json_to_send = []
    for chunk in file_details_json['chunks']:
        json_to_send.append({'chunk': chunk, 'peers': file_details_json['peers'],
                             'full_file_hash': file_details_json['full_hash']})
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(download_one_chunk, json_to_send)
        if False in res:
            return False
        else:
            return True


def download_one_chunk(chunk):
    chunk_size = request_chunk_size(chunk)
    if not chunk_size:
        return False


def request_chunk_size(chunk):
    request_chunk_size_json = {'full_hash': chunk['full_file_hash'],
                               'chunk_id': chunk['chunk']['id'],
                               'size': True}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_id = 0
    while peer_id < len(chunk['peer']):
        try:
            s.connect((json.dumps(request_chunk_size_json['peers'][peer_id]['ip']).replace('"', ""), 65432))
        except Exception:
            peer_id = peer_id + 1
            continue
        s.sendall(bytes(request_chunk_size_json, 'ascii'))
        try:
            received_data = int(s.recv(25))
            return received_data
        except Exception:
            peer_id = peer_id + 1
            continue
    return False
# def combine_chunks(file_details_json):


def request_file_from_peer(file_hash):
    file_details_json = json.loads(str(request_file_details_from_tracker(file_hash)))
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
            "chunk_id": file_details_json["chunks"][chunk_counter]["id"],
            "size_request": False}
        send_file_request_json = json.dumps(send_file_request_json)
        print(send_file_request_json)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((json.dumps(file_details_json["peers"]
                                  [peer_counter % len(file_details_json["peers"])]["ip"]).replace('"', ""), 65432))
        except Exception:
            peer_counter = peer_counter + 1
            continue
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
        # time.sleep(3)
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
