from socket import *
import sys
from select import select
from datetime import datetime
from chatroom import *

def chat(port, name):
    sockfd = socket(AF_INET, SOCK_STREAM)
    HOSTNAME, ListenPort = "", port
    sockfd.connect(("127.0.0.1", ListenPort))
    sockfd.send(name.encode())
    flag = 0
    while True:
        sockets_list = [sys.stdin, sockfd]
        readable, writable, exceptional = select(sockets_list, [] , [] , 0)  
        for socks in readable:
            if socks == sockfd:  
                message = socks.recv(2048).decode()
                if message == "close":
                    flag = 1
                    break  
                print(message)
            else:
                msg = sys.stdin.readline().strip('\n')
                if msg == "leave-chatroom":
                    message = "leave"
                    flag = 1
                elif msg == "detach":
                    message = "detach"
                    flag = 1
                else:
                    now = datetime.now()
                    time = now.strftime("%H:%M")
                    message = name + '[' + time + '] : ' 
                    message += msg
                sockfd.send(message.encode())
            if flag == 1:
                break
        if flag == 1:
            break
    
    sockfd.close()