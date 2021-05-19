#coding:utf-8

import socket

mysocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
mysocket.connect(('localhost',5566))

def send_socket(client):

    data=input("write a msg: ")
    data=data.encode("utf8")
    client.sendall(data)
 



while True:
	send_socket(mysocket)