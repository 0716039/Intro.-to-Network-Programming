#!/usr/bin/python3

from socket import *
from select import select
import threading
import sys
import json
from datetime import datetime
import globals

semaphore = threading.Semaphore(0)
list_of_clients = []
list_of_chats = []

def HandleClientMsg(sockfd, addr, owner):
    name = sockfd.recv(2048).decode()
    servmsg = '*' * 32 + "\n*** Welcome to the chatroom. ***\n" + '*' * 32
    sockfd.send(servmsg.encode())
    if len(list_of_chats) >= 3:
        servmsg = "\n" + list_of_chats[-3] + "\n" + list_of_chats[-2] + "\n" + list_of_chats[-1]
        sockfd.send(servmsg.encode())
    elif len(list_of_chats) == 2:
        servmsg = "\n" + list_of_chats[-2] + "\n" + list_of_chats[-1]
        sockfd.send(servmsg.encode())
    elif len(list_of_chats) == 1:
        servmsg = "\n" + list_of_chats[-1]
        sockfd.send(servmsg.encode())
    now = datetime.now()
    time = now.strftime("%H:%M")
    message = "sys" + "[" + time + "] : " + name + " join us."
    broadcasting(message, sockfd)
    while True:
        try:
            if message:
                message = sockfd.recv(2048).decode()
                message.strip()
                cmd = message.split(" ")[0]
                if cmd == "leave":
                    if name == owner:
                        
                        now = datetime.now()
                        time = now.strftime("%H:%M")
                        message = "sys" + "[" + time + "] : the chatroom is close." 
                        broadcasting(message, sockfd)
                        message = "close"
                        broadcasting(message, sockfd)
                        list_of_clients.clear()
                        globals.close = 1
                        
                        break
                    else:
                        
                        now = datetime.now()
                        time = now.strftime("%H:%M")
                        message = "sys" + "[" + time + "] : " + name + " leave us."
                        broadcasting(message, sockfd)
                        list_of_clients.remove(sockfd)
                        
                        break
                elif cmd == "detach":
                    if name == owner:
                        
                        now = datetime.now()
                        time = now.strftime("%H:%M")
                        message = "sys" + "[" + time + "] : " + name + " leave us."
                        broadcasting(message, sockfd)
                        list_of_clients.remove(sockfd)
                        
                        break
                list_of_chats.append(message)
                broadcasting(message, sockfd)
            else:
                remove(sockfd)
        except:
            continue
    sockfd.close()

def broadcasting(message, conn):  
    for clients in list_of_clients:  
        if clients!= conn:
            try:  
                clients.send(message.encode())  
            except:
                remove(clients)

def remove(conn):  
    if conn in list_of_clients:  
        list_of_clients.remove(conn)

def server(port, owner):
    HOSTNAME, ListenPort = "", port
    
    sockfd = socket(AF_INET, SOCK_STREAM)
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(('', ListenPort))
    sockfd.listen(10)
    semaphore.release()
    inputs = [sockfd]
    try:
        while True:
            readable, writable, exceptional = select(inputs, [], [], 0)
            for sockfd in readable:
                connfd, addr = sockfd.accept()
                list_of_clients.append(connfd)
                t = threading.Thread(target = HandleClientMsg, args = (connfd, addr, owner))
                t.daemon = True
                t.start()
    except KeyboardInterrupt:
        print("\nServer close.")
    for sockfd in inputs:
        sockfd.close()