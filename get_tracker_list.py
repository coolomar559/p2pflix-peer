import json
import os

from IPy import IP
import requests
import toml


def gui_add_ip_to_toml(input_ip):
    if not IP(input_ip):
        return "invalid IP."
    fp = open('./tracker.toml', 'r+')
    ips = fp.read()
    fp.close()
    ips = str(ips)
    try:
        ips = toml.loads(ips)
    except Exception:
        open('./tracker.toml', 'w').close()
    if ips != "":  # str(ips) not in ips['ips']:
        if input_ip not in ips['ip']:
            fp = open('./tracker.toml', 'w+')
            ips['ip'].append(input_ip)
            toml.dump(ips, fp)
            fp.close()
            return "It has been added"
        else:
            return "It is already in the toml file"
    else:
        fp = open('./tracker.toml', 'w+')
        ips = {"ip": [input_ip]}
        toml.dump(ips, fp)
        fp.close()


def get_t_list():
    list_of_ips = []
    try:
        fp = open('./tracker.toml', 'r+')
        tracker_content = fp.read()
        list_of_ips = toml.loads(tracker_content)
    except Exception:
        return False
    # list_of_ips = get_first_t()
    list_of_ips = add_all_trackers(list_of_ips)
    overwrite_ips_in_toml(list_of_ips)
    return list_of_ips


def overwrite_ips_in_toml(list_of_ips):
    my_dict = {'ip': list_of_ips}
    with open('./tracker.toml', 'w') as fp:
        toml.dump(my_dict, fp)


def add_all_trackers(list_of_ips):
    for ip in list_of_ips:
        try:
            r = requests.get('http://' + ip + "/tracker_list")
        except Exception:
            # list_of_ips.remove(ip)
            continue
        request_json = json.loads(r.text())
        if (request_json['success']):
            for new_ip in request_json['trackers']:
                if new_ip not in list_of_ips:
                    list_of_ips.append(new_ip)
    return list_of_ips


def get_first_t():
    if os.path.exists('./tracker.toml'):
        try:
            toml_file = open('./tracker.toml', 'r+')
        except Exception:
            return get_user_input_for_ip()
        toml_obj = toml.load(toml_file)
        toml_file.close()
        if 'ip' not in toml_obj:
            return get_user_input_for_ip()
        toml_file = open('./tracker.toml', 'r')
        return list(toml_obj['ip'])
    else:
        return get_user_input_for_ip()


def add_trackers(ip):
    while True:
        try:
            r = requests.get('http://' + ip + '/tracker_list')
            return r.text()
        except Exception:
            print()


def get_user_input_for_ip():
    print("Couldn't find a tracker.toml file in this directory. Please enter the IP of a tracker")
    while True:
        tracker_ip_from_user = input()
        try:
            IP(tracker_ip_from_user)
            return [tracker_ip_from_user]
        except Exception:
            print("invalid IP please try again")


if __name__ == "__main__":
    get_t_list()
