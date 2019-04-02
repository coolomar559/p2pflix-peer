from concurrent import futures
import hashlib
import os
import pickle
import socket

import constants
from get_tracker_list import get_local_tracker_list
import requests


def get_file_info(fhash):
    tracker_ips = get_local_tracker_list()
    for tracker_ip in tracker_ips:
        try:
            r = requests.get(
                f"http://{tracker_ip}:{constants.TRACKER_PORT}/file_by_hash/{fhash}",
                timeout=constants.REQUEST_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout, ValueError) as e:
            return {
                "success": False,
                "error": str(e),
            }

    return {
        "success": False,
        "error": "No trackers available",
    }


# Download the given file with the given number of threads
# Returns true on successful download and false otherwise
def download_file(file_details_json, num_of_threads=4):
    # Return false if we failed to download the chunks
    if not download_many(file_details_json, num_of_threads):
        return False

    # Combine the chunks and verify the file
    combine_chunks(file_details_json)
    return verify_full_file(file_details_json)


# Verify the given full file
# Returns true on successful validation and false otherwise
def verify_full_file(file_details_json):
    file_name = file_details_json['name']
    expected_hash = file_details_json['full_hash']
    block_size = 1000000
    sha256 = hashlib.sha256()

    with open(file_name, 'rb') as f:
        buf = f.read(block_size)
        while len(buf) > 0:
            sha256.update(buf)
            buf = f.read(block_size)

    return sha256.hexdigest() == expected_hash


# Download the given file using the given number of threads
# Returns True on successful download and False otherwise
def download_many(file_details_json, num_of_threads):
    workers = min(num_of_threads, len(file_details_json['chunks']))
    json_to_send = []

    for chunk in file_details_json['chunks']:
        json_to_send.append({'chunk': chunk, 'peers': file_details_json['peers'],
                             'full_file_hash': file_details_json['full_hash'],
                             'name': file_details_json['name']})

    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(download_one_chunk, json_to_send)
        if False in res:
            return False
        else:
            return True


# Combine the individual chunk files back into the original file
def combine_chunks(file_details_json):
    with open(file_details_json['name'], 'ab') as full_file:
        for chunk in file_details_json['chunks']:
            chunk_file = open(chunk['name'], 'rb')
            chunk_data = chunk_file.read()
            chunk_file.close()
            os.remove(chunk['name'])
            full_file.write(chunk_data)


# Attempt to download the given chunk from the list of peers and write the
# chunk to file.
# Returns True on success and False otherwise
def download_one_chunk(chunk):
    request_data = {
        'full_hash': chunk['full_file_hash'],
        'chunk_id': chunk['chunk']['id'],
    }

    for peer in chunk['peers']:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer['ip'], constants.PEER_PORT))

            # Send the request
            s.sendall(pickle.dumps(request_data))

            # Recieve the file size (or -1 for error)
            chunk_size = pickle.loads(s.recv(64))

            # Try next peer if there was an error
            if chunk_size == -1:
                continue

            # Recieve the file data
            chunk_data = recvall(s, chunk_size)

            # Try the next peer if we can't verify the chunk
            if not verify_chunk(chunk_data, chunk['chunk']['chunk_hash']):
                continue

            # Write the data to file
            with open(chunk['chunk']['name'], 'wb') as chunk_file:
                chunk_file.write(chunk_data)

            return True

    # Return false if we didn't successfully get the file from any peers
    return False


# Verify the given chunk against the expected hash
# Returns true on successful verification, and false otherwise
def verify_chunk(chunk_data, expected_hash):
    actual_hash = hashlib.sha256(chunk_data).hexdigest()
    if expected_hash == actual_hash:
        return True
    else:
        return False


# Recieve n bytes from the given socket
# Returns the read bytes
def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        data += packet

    return data
