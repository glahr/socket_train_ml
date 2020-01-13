# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:08:50 2020

@author: glahr
"""

import socket
import pickle

HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(1)

print('Esperando conexao (',orig,')')
con, cliente = tcp.accept()
print('Concetado por', cliente)


total_received = 0
msg_size = int(con.recv(1024))

con.send(str.encode('tamanho recebido ' + str(msg_size)))

print('msg_size',msg_size)
msg = bytes()
while total_received < msg_size:
    last_msg = con.recv(1024)
    msg = msg + last_msg
    total_received = total_received + len(last_msg)

print(cliente, pickle.loads(msg))
con.send(str.encode('oquei'))
print('Finalizando conexao do cliente', cliente)
con.close()