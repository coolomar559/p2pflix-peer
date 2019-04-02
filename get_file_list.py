import constants
from get_tracker_list import get_local_tracker_list
import requests


def get_file_list():
    tracker_ips = get_local_tracker_list()
    for tracker_ip in tracker_ips:
        try:
            r = requests.get(
                f"http://{tracker_ip}:{constants.TRACKER_PORT}/file_list",
                timeout=constants.REQUEST_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout, ValueError) as e:
            return {
                "success": False,
                "error": str(e),
            }

    return {
        "success": False,
        "error": "No trackers available",
    }
