#!/usr/bin/env python3

import socket
import sys
import json

import base64

HOST = "localhost"
PORT = 65432
counter = 0
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        conn, addr = s.accept()
        with conn:
            print("Connected by", addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    s.close()
                    break
                print("decoded data: " + data.decode('utf-8'))
                recv_json = json.loads(data.decode('ascii'))
                with open('vid/vid.mp4#'+json.dumps(recv_json["chunk_id"]),'rb') as f:
                    counter = counter + 1
                    conn.sendall(f.read())
                    
                s.close()
            
