from get_configs import get_configs, get_trackers
import requests


# Gets the list of trackers from tracker.toml,
# sends requests to ip's in the list until
# it gets a response
def send_request():

    config = get_configs()

    if config is None or 'guid' not in config:
        return {
            "success": False,
            "error": "You have no guid!",
        }

    ip_list = get_trackers()

    port = 42069
    for i in range(0, len(ip_list)):
        ip = ip_list[i]
        url = 'http://' + str(ip) + ':' + str(port) + '/peer_status' + '/' + config['guid']
        try:
            r = requests.get(url, timeout=1)
            if(r.status_code == requests.codes.ok):
                return r.json()
        except Exception:
            print(ip_list[i] + " did not respond!")
    print("there is no working tracker ip!")
    return {
            "success": False,
            "error": "Can't connect to any tracker",
        }


# Gets the peer guid from config file
# and queries tracker for peer's files and
# expected seq_number
# If no seq_number, returns an empty list
def get_status():

    response = send_request()
    print(response)
    return response
