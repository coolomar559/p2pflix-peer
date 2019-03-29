#!/usr/bin/env python3
from add_file import add_file_r
import fire
from get_file_list import request_file_from_peer, request_file_list
from listen import seed


def add_file(filename: str) -> None:
    add_file_r(filename)
    pass


def get_file_list():
    request_file_list()
    pass


def get_file(file_id: str) -> None:
    request_file_from_peer(file_id)
    pass


def listen():
    seed()
    pass


if __name__ == "__main__":
    fire.Fire({
        'add-file': add_file,
        'get-file-list': get_file_list,
        'get-file': get_file,
        'listen': listen,
    })
