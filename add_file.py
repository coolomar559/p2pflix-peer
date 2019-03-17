import requests


def add_my_file(filename):
    j = {"name": "my file name "}
    r = requests.post('http://localhost:42069/add_file', j)
    print()
    print(r.text)
