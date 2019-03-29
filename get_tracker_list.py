import json
import os

from IPy import IP
import requests
import toml


def get_t_list():
    list_of_ips = get_first_t()
    list_of_ips = add_all_trackers(list_of_ips)
    toml_file = open('./tracker.toml', 'r')
    print("content of the toml file after getting all tracker info:  " + toml_file.read())
    overwrite_ips_in_toml(list_of_ips)
    return list_of_ips


def overwrite_ips_in_toml(list_of_ips):
    toml_file = open('./tracker.toml', 'r+')
    toml_content = toml_file.read()
    print("content of the toml file before writing to it: " + toml_content)
    toml_content = toml.loads(toml_content)
    toml_content['trackers'] = list_of_ips
    toml_file = toml_file.write(toml.dumps(toml_content))


def add_all_trackers(list_of_ips):
    for ip in list_of_ips:
        try:
            r = requests.get('http://' + ip + "/tracker_list")
        except Exception:
            list_of_ips.remove(ip)
            continue
        request_json = json.loads(r.text())
        if (request_json['success']):
            for new_ip in request_json['trackers']:
                if new_ip not in list_of_ips:
                    list_of_ips.append(new_ip)
    return list_of_ips


def get_first_t():
    if os.path.exists('./tracker.toml'):
        toml_file = open('./tracker.toml', 'r')
        toml_obj = toml.load(toml_file)
        toml_file.close()
        print("length of ops in tracker.toml: " + str(len(toml_obj['servers']['ip'])))
        toml_file = open('./tracker.toml', 'r')
        print("content of the toml file after initial read: " + toml_file.read())
        return list(toml_obj['servers']['ip'])
    else:
        return get_user_input_for_ip()


def add_trackers(ip):
    while True:
        try:
            r = requests.get('http://' + ip + '/tracker_list')
            return r.text()
        except Exception:
            print(Exception)


def get_user_input_for_ip():
    print("Couldn't find a tracker.toml file in this directory. Please enter the IP of a tracker")
    while True:
        tracker_ip_from_user = input()
        if IP(tracker_ip_from_user):
            return [tracker_ip_from_user]
            break
        else:
            print("invalid IP please ")


if __name__ == "__main__":
    get_t_list()
