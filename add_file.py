import hashlib
import json
import os
import shutil

from get_configs import add_seq, get_configs, update_seq
import requests


CHUNK_SIZE = 1000000
APP_DIR = os.getcwd()
CHUNK_DIR = os.path.join(os.getcwd(), 'files/')
BLOCK_SIZE = 4096


# Returns hash of the full file
def get_full_hash(filename):
    full_hash = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(BLOCK_SIZE), b''):
            full_hash.update(block)
    return full_hash.hexdigest()


# 1. Chunks the file into smaller parts
# 2. Saves the chunks into the 'Files' directory
# 3. Returns the hashes of the chunk files
def chunk_file(filename, fhash):
    with open(filename, 'rb') as f:

        # Create directory to store chunks
        new_dir = CHUNK_DIR + fhash
        try:
            os.mkdir(new_dir)
        except Exception:
            print('Could not create directory!')
            exit(-1)

        # Chunk file, save chunks to chunk directory and
        # collect file data for all the chunks (name, hash, id)
        chunks = []
        chunk_id = 0
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
            chunk_data = {}
            chunk_data['id'] = chunk_id
            chunk_data['name'] = fhash + '#' + str(chunk_id)
            chunk_data['hash'] = hashlib.sha256(chunk).hexdigest()
            chunks.append(chunk_data)

            chunk_filename = new_dir + '/' + chunk_data['name']
            chunk_file = open(chunk_filename, 'wb')
            chunk_file.write(chunk)
            chunk_file.close()

            chunk_id += 1

    return chunks


def send_request(data, ip='127.0.0.1'):
    port = 42069
    url = 'http://' + str(ip) + ':' + str(port) + '/add_file'

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, json.dumps(data), headers=headers)
    print(r.json())

    return r.json()


def add_file_r(filename):

    # If file directory does not exists, create one
    if (not os.path.exists('files')):
        os.mkdir('files')

    config = get_configs() if os.path.exists('config.ini') else add_seq()

    data = {}
    data['guid'] = None if 'guid' not in config else config['guid']
    data['seq_number'] = int(config['seq_number'])
    data['name'] = filename
    fullhash = get_full_hash(filename)
    data['full_hash'] = fullhash
    data['chunks'] = chunk_file(filename, fullhash)

    response = send_request(data)
    if(not response['success']):
        shutil.rmtree('files/' + fullhash)
    else:
        update_seq(response['guid'], data['seq_number'])
