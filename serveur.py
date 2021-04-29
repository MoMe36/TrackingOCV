#coding:utf-8
import socket

socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host,port=('',5566)
socket.bind((host,port))
print("le serveur est démarer")

while True:
	socket.listen()
	conn,adresse=socket.accept()

	print(" Listening ...")
	data=conn.recv(1024)
	data=data.decode("utf-8")
	print(data)

conn.close()
socket.close()