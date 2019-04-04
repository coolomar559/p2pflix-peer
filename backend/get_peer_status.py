from backend import constants
from backend.get_configs import get_configs
from backend.get_tracker_list import get_local_tracker_list
import requests


# Gets the list of trackers from tracker.toml,
# sends requests to ip's in the list until
# it gets a response
def get_status():

    config = get_configs()

    if config is None or "guid" not in config:
        return {
            "success": False,
            "localerror": True,
            "error": "You have no guid!",
        }

    ip_list = get_local_tracker_list()
    for ip in ip_list:
        try:
            r = requests.get(
                f"http://{ip}:{constants.TRACKER_PORT}/peer_status/{config['guid']}",
                timeout=constants.REQUEST_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout, ValueError):
            continue

    return {
            "success": False,
            "localerror": True,
            "error": "Can't connect to any tracker",
        }
