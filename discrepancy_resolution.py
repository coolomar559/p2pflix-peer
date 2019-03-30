import hashlib
import os

# from deregister_file_by_hash import deregister_file
from get_configs import get_configs
from get_file_list import request_file_list


CHUNK_DIR = os.path.join(os.getcwd(), 'files/')


def remove_from_tracker(file_hash):
    # deregister_file(file_hash)
    print("REMOVING " + file_hash + " FROM TRACKER")


def add_to_tracker(file_hash, data):

    data['full_hash'] = file_hash
    chunks = []
    file_path = CHUNK_DIR + file_hash
    for chunk_name in os.listdir(file_path):
        chunk_path = file_path + '/' + chunk_name
        with open(chunk_path, 'rb') as chunk_file:
            chunk = chunk_file.read()
            chunk_data = {}
            chunk_data['id'] = chunk_name.split("#")[1]
            chunk_data['name'] = chunk_name
            chunk_data['hash'] = hashlib.sha256(chunk).hexdigest()
            chunks.append(chunk_data)
            print(chunk_data)
    print("ADDING " + file_hash + " TO TRACKER")


def resolve():

    tracker_dict = request_file_list()
    peer_list = os.listdir('files')
    tracker_list = []
    for file in tracker_dict:
        tracker_list.append(file['full_hash'])

    config = get_configs()

    data = {}
    data['guid'] = config['guid']
    data['seq_number'] = int(config['seq_number'])
    # data['name'] = filename
    # fullhash = get_full_hash(filename)
    # data['full_hash'] = fullhash
    # data['chunks'] = chunk_file(filename, fullhash)


    # Remove files from tracker that the peer doesnt have
    for file in tracker_list:
        if file in peer_list:
            peer_list.remove(file)
        else:
            remove_from_tracker(file)

    for file in peer_list:
        if file not in tracker_list:
            add_to_tracker(file, data)
