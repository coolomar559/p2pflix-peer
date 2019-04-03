#!/usr/bin/env python3
from pprint import pprint

from backend import constants
from backend.add_file import add_file_r
from backend.deregister_file_by_hash import deregister_file
from backend.discrepancy_resolution import resolve
from backend.get_file import download_file, get_file_info
from backend.get_file_list import get_file_list
from backend.get_peer_status import get_status
from backend.get_tracker_list import update_primary_tracker
from backend.listen import SeedThread
import fire


def add_file(file_name):
    result = add_file_r(file_name)
    if result["success"]:
        print("Successfully added file to tracker")
    else:
        print(result["error"])


def resolve_discrepancy():
    pprint(resolve())


def deregister_file_by_hash(file_hash):
    pprint(deregister_file(file_hash))


def list_files():
    file_list = get_file_list()
    if file_list["success"]:
        pprint(file_list["files"])
    else:
        print(file_list["error"])


def get_peer_status():
    pprint(get_status())


def get_file(file_hash):
    file_info = get_file_info(file_hash)

    if not file_info["success"]:
        print(file_info["error"])
        return

    download_result = download_file(file_info, download_progress_callback)
    if download_result["success"]:
        print("File downloaded successfully")
    else:
        print(download_result["error"])


def listen():
    seeder = SeedThread(seeder_listening, seeder_error, seeder_shutdown)
    seeder.daemon = True
    seeder.start()

    try:
        # Wait on an event to get an endless wait that can be interrupted
        seeder.stopped_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        seeder.stop()
        seeder.join()


def set_primary_tracker(tracker_ip):
    result = update_primary_tracker(tracker_ip)
    if result["success"]:
        print("Successfully updated primary tracker")
    else:
        print(result["error"])


def seeder_listening():
    print(f"Listening on port {constants.PEER_PORT}")


def seeder_error(error):
    print(error)


def seeder_shutdown():
    print("\nSeeder shut down")


def download_progress_callback(success):
    print(f"Got chunk progress callback: {success}")


if __name__ == "__main__":
    fire.Fire({
        'add-file': add_file,
        'list-files': list_files,
        'get-file': get_file,
        'listen': listen,
        'deregister-file': deregister_file_by_hash,
        'get-peer-status': get_peer_status,
        'discrepancy-resolution': resolve,
        'set-primary-tracker': set_primary_tracker,
    })
