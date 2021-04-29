#coding:utf-8

import socket

socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:

    socket.connect(('localhost',5566))
    print("connected client!")
    data=input("write a message :")
    data=data.encode("utf8")
    socket.sendall(data)



except:
	print("communication to the server failed")

finally:
	socket.close()