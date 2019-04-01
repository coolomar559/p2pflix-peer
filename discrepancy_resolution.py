import os
import shutil

from deregister_file_by_hash import deregister_file
from get_configs import get_configs, update_seq
from get_file_list import get_file_list
from get_peer_status import get_status


CHUNK_DIR = os.path.join(os.getcwd(), 'files/')


def resolve():

    # Get current and expected seq_number
    configs = get_configs()
    actual_seq = int(configs['seq_number'])
    expected_seq = get_status()['expected_seq_number']

    # If there is a discrepancy, fix it on peer side
    if(actual_seq != expected_seq):
        update_seq(configs['guid'], expected_seq-1)

    # Get tracker and peer file lists
    tracker_dict = get_file_list()['files']
    peer_list = os.listdir('files')

    # Remove files from tracker that the peer doesn't have
    for file in tracker_dict:
        if file['full_hash'] in peer_list:
            peer_list.remove(file['full_hash'])
        else:
            deregister_file(file['full_hash'])

    # Remove files from peer the tracker doesn't have
    tracker_list = []
    for file in tracker_dict:
        tracker_list.append(file['full_hash'])
    for file in peer_list:
        if file not in tracker_list:
            try:
                shutil.rmtree(CHUNK_DIR + file)
            except Exception:
                return {
                    "success": False,
                    "error": "could not remove file <" + file + ">",
                }

    return {"success": True}
