import configparser
import hashlib
import json
import os
import shutil

import requests


CHUNK_SIZE = 1000000
APP_DIR = os.getcwd()
CHUNK_DIR = os.path.join(os.getcwd(), 'files/')
BLOCK_SIZE = 4096


# Reads the 'config.ini' to get configurations
# and returns them in a dict
# Creates a config file if one does not exit
def get_configs():
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        return dict(config.items('p2pflix'))
    except Exception:
        config = configparser.ConfigParser()
        config.add_section('p2pflix')
        config.set('p2pflix', 'seq_number', '0')
        with open('config.ini', 'w') as f:
            config.write(f)
        return dict(config.items('p2pflix'))


# Reads config file, updates seq_number,
# writes guid if it does not exist
# and writes file
def update_seq(guid, seq_number):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('p2pflix', 'seq_number', str(seq_number+1))
    if 'seq_number' not in config:
        config.set('p2pflix', 'guid', guid)
    with open('config.ini', 'w') as f:
        config.write(f)


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

    return r.json()


def add_file_r(filename):

    # If file directory does not exists, create one
    if (not os.path.exists('files')):
        os.mkdir('files')

    config = get_configs()

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
