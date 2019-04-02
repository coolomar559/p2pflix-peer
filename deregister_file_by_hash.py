import os
import shutil

import constants
from get_configs import get_configs, update_seq
from get_tracker_list import get_local_tracker_list
import requests


# Gets the list of trackers from tracker.toml,
# sends requests to ip's in the list until
# it gets a response
def send_request(data, ip='127.0.0.1'):

    ip_list = get_local_tracker_list()
    for ip in ip_list:
        try:
            r = requests.delete(
                f"http://{ip}:{constants.TRACKER_PORT}/deregister_file_by_hash",
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


def deregister_file(file_hash):

    config = get_configs()

    data = {}
    data['file_hash'] = file_hash
    data['guid'] = config['guid']
    data['seq_number'] = int(config['seq_number'])

    if (send_request(data)['success']):
        update_seq(config['guid'], int(config['seq_number']))
        if(os.path.exists('files/' + file_hash)):
            shutil.rmtree('files/' + file_hash)
        return {"sucess": True}

    return {
        "success": False,
        "error": "could not remove file <" + file_hash + ">",
    }
