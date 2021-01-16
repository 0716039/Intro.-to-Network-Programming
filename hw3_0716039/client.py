#!/usr/bin/python3

from socket import *
import sys
import json
from chat import *
from chatroom import *
import threading
import globals

UseUDP = ["register", "whoami", "list-chatroom"]

class ClientService(object):
    def __init__(self, IP, Port):
        self.IP = IP
        self.Port = Port
        self.sessionID = -1

    def UDPsender(self, msg):
        sockfd = socket(AF_INET, SOCK_DGRAM)
        msg2serv = json.dumps({'msg': msg, 'sid': self.sessionID})
        sockfd.sendto(msg2serv.encode(), (self.IP, self.Port))
        servmsg, servaddr = sockfd.recvfrom(1024)
        content = json.loads(servmsg.decode())
        self.sessionID = content["sid"]
        sockfd.close()
        return content["msg"]

    def TCPsender(self, msg):
        sockfd = socket(AF_INET, SOCK_STREAM)
        sockfd.connect((self.IP, self.Port))
        msg2serv = json.dumps({'msg': msg, 'sid': self.sessionID})
        sockfd.send(msg2serv.encode())
        servmsg = sockfd.recv(1024).decode()
        content = json.loads(servmsg)
        self.sessionID = content["sid"]
        sockfd.close()
        return content["msg"]


def main():
    if len(sys.argv) != 3:
        print(f"\tUsage {sys.argv[0]} <IP> <Port>")
        exit(-1)
    Client = ClientService(sys.argv[1], int(sys.argv[2]))
    msg = Client.UDPsender("INITIAL")
    if msg:
        print(msg)
    else:
        print("Failed to connect to {IP}:{Port}")
        exit(-1)
    send = 0
    while True:
        msg = input("% ")
        cmd = msg.split(" ")[0]
        if cmd in UseUDP:
            servmsg = Client.UDPsender(msg)
        else:
            servmsg = Client.TCPsender(msg)
        if msg == "exit":
            break
        cmd_chat = servmsg.split(" ")[0]
        if cmd_chat != "join" and cmd_chat != "attach":
            print(servmsg)
        
        flag = 0
        if servmsg == "start to create chatroom...":
            globals.close = 0
            flag = 1
            if globals.myport != 0:
                port = globals.myport
                name = Client.UDPsender("whoami")
                t2 = threading.Thread(target = chat, args = (port, name, ))
                t2.daemon = True
                t2.start()
                t2.join()
            else:
                port = int(msg.split(" ")[1])
                globals.myport = port
                name = Client.UDPsender("whoami")
                t1 = threading.Thread(target = server, args = (port, name, ))
                t1.daemon = True
                t1.start()
                semaphore.acquire()
                t2 = threading.Thread(target = chat, args = (port, name, ))
                t2.daemon = True
                t2.start()
                t2.join()
        if cmd_chat == "attach":
            flag = 1
            port = globals.myport
            name = Client.UDPsender("whoami")
            t = threading.Thread(target = chat, args = (port, name, ))
            t.daemon = True
            t.start()
            t.join()
        if cmd_chat == "join":
            flag = 1
            port = int(servmsg.split(" ")[1])
            name = Client.UDPsender("whoami")
            t = threading.Thread(target = chat, args = (port, name, ))
            t.daemon = True
            t.start()
            t.join()
        if flag == 1:
            print("Welcome back to BBS.")
        if globals.close == 1 and msg != "logout":
            Client.TCPsender("leave-chatroom")
        
if __name__ == "__main__":
    globals.initialize()
    main()
