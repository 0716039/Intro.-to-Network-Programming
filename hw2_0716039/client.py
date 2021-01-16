#!/usr/bin/python3

from socket import *
import sys
import json
 
UseTCP = ["login", "logout", "list-user", "exit", "create-board", "create-post", "list-board", 
          "list-post", "read", "delete-post", "update-post", "comment"]

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

    while True:
        msg = input("% ")
        cmd = msg.split(" ")[0]
        if cmd in UseTCP:
            servmsg = Client.TCPsender(msg)
        else:
            servmsg = Client.UDPsender(msg)
        if msg == "exit":
            break
        print(servmsg)


if __name__ == "__main__":
    main()
