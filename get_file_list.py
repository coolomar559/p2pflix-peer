import ipaddress
import json

import requests


def request_file_list(**kwargs):
    my_ip = str()

    for key, _value in kwargs.items():
        if key == 'ip' and ipaddress.ip_address(kwargs['ip']):
            print(kwargs['ip'])
            my_ip = kwargs['ip']
    if not my_ip:
        my_ip = "localhost"
    r = requests.get('http://' + str(my_ip) + ':42069/file_list')
    r_json = r.json()
    print(r)
    print()
    print(json.dumps(r_json, indent=4))
