import shutil

from get_configs import get_configs, get_trackers, update_seq
import requests


# Gets the list of trackers from tracker.toml,
# sends requests to ip's in the list until
# it gets a response
def send_request(data, ip='127.0.0.1'):

    ip_list = get_trackers()

    port = 42069
    for i in range(0, len(ip_list)):
        ip = ip_list[i]
        url = 'http://' + str(ip) + ':' + str(port) + '/deregister_file_by_hash'
        r = requests.delete(url, json=data)
        if(r.status_code == requests.codes.ok):
            print(r.json())
            return r.json()

    print("there is no working tracker ip!")


def deregister_file(file_hash):

    config = get_configs()

    data = {}
    data['file_hash'] = file_hash
    data['guid'] = config['guid']
    data['seq_number'] = int(config['seq_number'])

    if (send_request(data)['success'] is True):
        update_seq(config['guid'], int(config['seq_number']))
        shutil.rmtree('files/' + file_hash)
