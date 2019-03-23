import configparser
import hashlib
import json
import os
import uuid
from tkinter import Tk, filedialog

import requests


CHUNK_SIZE = 1000000
# CHUNK_DIR = '/home/ugb/rehmanz/Desktop/559/Files/'
APP_DIR = '/home/ugb/rehmanz/p2pflix/'
CHUNK_DIR = '/home/ugb/rehmanz/p2pflix/Files/'
BLOCK_SIZE = 4096


# Gets file name through dialog UI
# Returns: name of selected file
def get_filename():
    Tk().withdraw()
    filename = filedialog.askopenfilename()
    return filename


# Reads the 'config.ini' to get configurations
# and returns them in a dict
# Creates a config file if one does not exit
def get_configs():
    try:
        config = configparser.ConfigParser()
        config.read(APP_DIR + 'config.ini')
        return dict(config.items('p2pflix'))
    except Exception:
        print('config.ini file not set, creating a new one.')
        config_file = open(APP_DIR + 'config.ini', 'w')
        config.add_section('p2pflix')
        config.set('p2pflix', 'guid', str(uuid.uuid4()))
        config.set('p2pflix', 'seq_number', '0')
        config.write(config_file)
        return dict(config.items('p2pflix'))


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
def chunk_file(filename):

    with open(filename, 'rb') as f:

        # Create directory to store chunks
        new_dir = CHUNK_DIR + filename.split('.')[0]
        try:
            os.mkdir(new_dir)
        except Exception:
            print('This file already exists!!')
            exit(-1)

        # Chunk file, save chunks to chunk directory and
        # collect file data for all the chunks (name, hash, id)
        chunks = []
        chunk_id = 0
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
            chunk_data = {}
            chunk_data['id'] = chunk_id
            chunk_data['name'] = filename + '#' + str(chunk_id)
            chunk_data['hash'] = hashlib.sha256(chunk).hexdigest()
            chunks.append(chunk_data)

            chunk_filename = new_dir + '/' + chunk_data['name']
            chunk_file = open(chunk_filename, 'wb')
            chunk_file.write(chunk)
            chunk_file.close()

            chunk_id += 1

    return chunks


def add_guid():

    return None


def add_file_r(filename):

    config = get_configs()

    data = {}
    data['guid'] = None
    # data['guid'] = config['guid']
    data['seq_number'] = int(config['seq_number'])
    data['name'] = filename
    data['full_hash'] = get_full_hash(filename)
    data['chunks'] = chunk_file(filename)
    print(json.dumps(data, indent=4))

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post('http://127.0.0.1:42069/add_file', json.dumps(data), headers=headers)
    print(json.dumps(r.text, indent=4))

    if(data['guid'] is None):
        add_guid()