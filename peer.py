#!/usr/bin/env python3
from add_file import add_my_file

import fire

from get_file_list import request_file_list, request_file_from_peer


def add_file(filename: str) -> None:
    add_my_file(filename)
    pass


def get_file_list():
    request_file_list()
    pass


def get_file(file_id: int) -> None:
    request_file_from_peer(file_id)
    pass


def listen():
    pass


if __name__ == "__main__":
    fire.Fire({
        'add-file': add_file,
        'get-file-list': get_file_list,
        'get-file': get_file,
        'listen': listen,
    })
