#!/usr/bin/env python3
import fire
import listen


def add_file(filename: str) -> None:
    pass


def get_file_list():
    pass


def get_file(file_id: int) -> None:
    pass


def listen():
    listen.seed()


if __name__ == "__main__":
    fire.Fire({
        'add-file': add_file,
        'get-file-list': get_file_list,
        'get-file': get_file,
        'listen': listen,
    })
