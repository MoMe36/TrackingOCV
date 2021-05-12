#coding:utf-8
import socket

def strat_serveur():

	serveur=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	host,port=('',5566)
	serveur.bind((host,port))
	print("le serveur est démarer")
	serveur.listen()
	conn,adresse=serveur.accept()

	while True:

		data=conn.recv(2048)
		data=data.decode("utf-8")
		print(data)
	conn.close()
	serveur.close()




strat_serveur()