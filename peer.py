#!/usr/bin/env python3
from add_file import add_file_r
from deregister_file_by_hash import deregister_file
from discrepancy_resolution import resolve
import fire
from get_file_list import request_file_from_peer, request_file_list
from get_peer_status import get_status
from listen import seed


def add_file(file_name: str) -> None:
    add_file_r(file_name)


def resolve_discrepancy():
    resolve()


def deregister_file_by_hash(file_hash: str) -> None:
    deregister_file(file_hash)


def get_file_list():
    request_file_list()


def get_peer_status():
    get_status()


def get_file(file_id: str) -> None:
    request_file_from_peer(file_id)


def listen():
    seed()


if __name__ == "__main__":
    fire.Fire({
        'add-file': add_file,
        'get-file-list': get_file_list,
        'get-file': get_file,
        'listen': listen,
        'deregister-file-by-hash': deregister_file_by_hash,
        'get-peer-status': get_peer_status,
        'discrepancy-resolution': resolve,
    })
