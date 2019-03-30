from get_configs import get_configs
import requests
import toml


# Gets the list of trackers from tracker.toml,
# sends requests to ip's in the list until
# it gets a response
def send_request():

    config = get_configs()

    if 'guid' not in config:
        return []

    toml_file = open('./tracker.toml', 'r')
    toml_obj = toml.load(toml_file)
    ip_list = list(toml_obj['ip'])

    port = 42069
    for i in range(0, len(ip_list)):
        ip = ip_list[i]
        url = 'http://' + str(ip) + ':' + str(port) + '/peer_status' + '/' + config['guid']
        r = requests.get(url)
        if(r.status_code == requests.codes.ok):
            return r.json()

    print("there is no working tracker ip!")
    return []


# Gets the peer guid from config file
# and queries tracker for peer's files and
# expected seq_number
# If no seq_number, returns an empty list
def get_status():

    response = send_request()
    print(response)
    return response
