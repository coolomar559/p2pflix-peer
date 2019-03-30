from get_file_list import request_file_list
import os


def resolve():

    tracker_list = request_file_list()
    peer_list = os.listdir('files')
    print(peer_list)
