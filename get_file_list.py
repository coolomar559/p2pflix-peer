import requests
import json
import ipaddress

def requestFileList(**kwargs):
    My_ip = str()

    for key, value in kwargs.items():
        if key is 'ip' and ipaddress.ip_address(kwargs['ip']):
            print(kwargs['ip'])
            My_ip = kwargs['ip']
            
    if not My_ip:
        My_ip = "localhost"
    r = requests.get('http://' + str(My_ip) + ':42069/list_files')
    rJson = r.json()
    print(r)
    print()
    print(json.dumps(rJson, indent = 4))

