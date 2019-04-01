from get_configs import get_configs, get_trackers
import requests


# Gets the list of trackers from tracker.toml,
# sends requests to ip's in the list until
# it gets a response
def send_status():

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
                return {"sucess": True}
        except Exception:
            pass
    return {
            "success": False,
            "error": "Can't connect to any tracker",
        }
