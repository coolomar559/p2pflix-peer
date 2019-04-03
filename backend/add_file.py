import hashlib
import os
from pathlib import Path
import shutil

from backend import constants
from backend.get_configs import add_seq, get_configs, update_seq
from backend.get_tracker_list import get_local_tracker_list
import requests


# Returns hash of the full file
def get_full_hash(filename):
    full_hash = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(constants.BLOCK_SIZE), b''):
            full_hash.update(block)
    return full_hash.hexdigest()


# 1. Chunks the file into smaller parts
# 2. Saves the chunks into the 'Files' directory
# 3. Returns the hashes of the chunk files
def chunk_file(filename, fhash):
    with open(filename, 'rb') as f:

        # Create directory to store chunks
        new_dir = Path(constants.CHUNK_DIRECTORY) / fhash
        new_dir.mkdir(parents=True, exist_ok=True)

        # Chunk file, save chunks to chunk directory and
        # collect file data for all the chunks (name, hash, id)
        chunks = []
        chunk_id = 0
        for chunk in iter(lambda: f.read(constants.CHUNK_SIZE), b''):
            chunk_data = {}
            chunk_data['id'] = chunk_id
            chunk_data['name'] = fhash + '#' + str(chunk_id)
            chunk_data['hash'] = hashlib.sha256(chunk).hexdigest()
            chunks.append(chunk_data)

            chunk_filename = new_dir / chunk_data['name']
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)

            chunk_id += 1

    return chunks


def send_request(data):
    ip_list = get_local_tracker_list()
    for ip in ip_list:
        try:
            r = requests.post(
                f"http://{ip}:{constants.TRACKER_PORT}/add_file",
                timeout=constants.REQUEST_TIMEOUT,
                json=data,
            )
            r.raise_for_status()
            return r.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout, ValueError):
            continue

    return {
        'success': False,
        'error': "No trackers available",
    }


def add_file_r(filename):
    file = Path(filename)
    if not file.is_file():
        return {
            "success": False,
            "error": "File does not exist",
        }

    config = get_configs() if os.path.exists('config.ini') else add_seq()

    data = {}
    data['guid'] = None if 'guid' not in config else config['guid']
    data['seq_number'] = int(config['seq_number'])
    data['name'] = file.name
    fullhash = get_full_hash(filename)
    data['full_hash'] = fullhash
    data['chunks'] = chunk_file(filename, fullhash)

    response = send_request(data)
    if(not response['success']):
        shutil.rmtree('files/' + fullhash)
    else:
        update_seq(response['guid'], data['seq_number'])

    return response
