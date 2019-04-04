import ipaddress
from pathlib import Path
import pickle

from backend import constants
import requests


TRACKER_FILE = "./tracker_list.dat"


# creates a new local tracker initialized with a placeholder local
def create_local_tracker_list():
    tracker_file_path = Path(TRACKER_FILE)

    with tracker_file_path.open(mode="wb") as tracker_file:
        tracker_data = {
            "primary": None,
            "backups": [],
        }
        pickle.dump(tracker_data, tracker_file)

    return


# gets a list of local trackers
def get_local_tracker_list():
    tracker_file_path = Path(TRACKER_FILE)

    if(not tracker_file_path.is_file()):
        create_local_tracker_list()

    with tracker_file_path.open(mode="rb") as tracker_file:
        tracker_data = pickle.load(tracker_file)
        primary_ip = tracker_data["primary"]
        ip_list = tracker_data["backups"]

        if(primary_ip is not None):
            ip_list.insert(0, primary_ip)

    return ip_list


# adds a new tracker ip to the local list
def add_tracker_ip_local(ip):
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        return False

    tracker_file_path = Path(TRACKER_FILE)

    if(not tracker_file_path.is_file()):
        create_local_tracker_list()

    with tracker_file_path.open(mode="r+b") as tracker_file:
        tracker_data = pickle.load(tracker_file)
        tracker_data["backups"].append(ip)
        tracker_file.seek(0)
        pickle.dump(tracker_data, tracker_file)

    return True


# changes the primary tracker in the local list
def update_primary_tracker(new_primary_ip):
    try:
        ipaddress.IPv4Address(new_primary_ip)
    except ValueError:
        return {
            "success": False,
            "error": "Invalid ip address",
        }

    tracker_file_path = Path(TRACKER_FILE)

    if(not tracker_file_path.is_file()):
        create_local_tracker_list()

    pull_response = pull_remote_tracker_list(new_primary_ip)

    if(not pull_response["success"]):
        return {
            "success": False,
            "error": "Error pulling tracker list from tracker",
        }

    with tracker_file_path.open("r+b") as tracker_file:
        tracker_data = pickle.load(tracker_file)
        tracker_data["primary"] = new_primary_ip
        tracker_data["backups"] = [t["ip"] for t in pull_response["trackers"]]

        tracker_file.seek(0)
        pickle.dump(tracker_data, tracker_file)

    return {
        "success": True,
    }


# gets the tracker list from the primary tracker
def pull_remote_tracker_list(tracker_ip):
    try:
        r = requests.get(
            f"http://{tracker_ip}:{constants.TRACKER_PORT}/tracker_list",
            timeout=constants.REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except (requests.HTTPError, requests.ConnectionError, requests.Timeout, ValueError) as e:
        return {
            "success": False,
            "error": str(e),
        }
