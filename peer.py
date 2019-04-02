#!/usr/bin/env python3
from pprint import pprint
from threading import Event

from add_file import add_file_r
import constants
from deregister_file_by_hash import deregister_file
from discrepancy_resolution import resolve
import fire
from get_file import download_file, get_file_info
from get_file_list import get_file_list
from get_peer_status import get_status
from listen import SeedThread


def add_file(file_name: str) -> None:
    add_file_r(file_name)


def resolve_discrepancy():
    resolve()


def deregister_file_by_hash(file_hash: str) -> None:
    deregister_file(file_hash)


def list_files():
    file_list = get_file_list()
    if file_list["success"]:
        pprint(file_list["files"])
    else:
        print(file_list["error"])


def get_peer_status():
    get_status()


def get_file(fhash):
    file_info = get_file_info(fhash)

    if not file_info["success"]:
        print(file_info["error"])

    if download_file(file_info):
        print("File downloaded successfully")
    else:
        print("There was an error downloading the file")


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


def seeder_listening():
    print(f"Listening on port {constants.PEER_PORT}")


def seeder_error(error):
    print(error)


def seeder_shutdown():
    print("\nSeeder shutting down")


if __name__ == "__main__":
    fire.Fire({
        'add-file': add_file,
        'list-files': list_files,
        'get-file': get_file,
        'listen': listen,
        'deregister-file-by-hash': deregister_file_by_hash,
        'get-peer-status': get_peer_status,
        'discrepancy-resolution': resolve,
    })
