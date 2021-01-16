#!/usr/bin/python3

from socket import *
from select import select
import threading
import sys
import json
import time

lock = threading.Lock()
sn = 0

class Board(object):
    def __init__(self):
        self.name = ""
        self.moderator = ""
        self.post_ids = []

class Comment(object):
    def __init__(self):
        self.content = ""
        self.author = ""

class Post(object):
    def __init__(self):
        self.title = ""
        self.content = ""
        self.author = ""
        self.date = ""
        self.comment = [] 

class Chatroom(object):
    def __init__(self):
        self.creator = ""
        self.status = ""
        self.port = 0

class ServerService(object):
    global sn
    
    def __init__(self):
        self.Session = {}
        self.user_info = {}
        self.user_email = {}
        self.board_info = {}
        self.post_info = {}
        self.comment_info = {}
        self.chatroom_info = {}
        self.bd = 0
        self.sn = 0
        self.cm = 0
        self.cr = 0

    def HandleTCP(self, sockfd, saddr):
        msg = sockfd.recv(1024).decode()
        servmsg = self.HandleClientMsg(msg, saddr)
        sockfd.send(servmsg.encode())
        sockfd.close()
    
    def HandleUDP(self, sockfd):
        msg, addr = sockfd.recvfrom(1024)
        msg = msg.decode()
        servmsg = self.HandleClientMsg(msg, addr)
        sockfd.sendto(servmsg.encode(), (addr[0], addr[1]))
    
    def HandleClientMsg(self, msg, addr):
        content = json.loads(msg)
        Arg, sessionID = content["msg"].split(), content["sid"]
        servmsg, cmd = "", Arg[0]
        if cmd == "INITIAL" and sessionID == -1:
            print("New connection.")
            sessionID = len(self.Session)
            self.Session[sessionID] = []
            servmsg = '*' * 32 + "\n** Welcome to the BBS server. **\n" + '*' * 32
        elif cmd == "register":
            lock.acquire()
            if len(Arg) != 4:
                servmsg = "Usage: register <username> <email> <password>"
            else:
                if self.user_info.get(Arg[1]) != None:
                    servmsg = "Username is already used."
                else:
                    self.user_info[Arg[1]] = Arg[3]
                    self.user_email[Arg[1]] = Arg[2]
                    servmsg = "Register successfully."
            lock.release()
        elif cmd == "login":
            lock.acquire()
            if len(Arg) != 3:
                servmsg = "Usage: login <username> <password>"
            else:
                if len(self.Session[sessionID]) and Arg[1] == self.Session[sessionID][-1][0]:
                    servmsg = "Please logout first."
                else:
                    if self.user_info.get(Arg[1]) != None:
                        if Arg[2] == self.user_info[Arg[1]]:
                            self.Session[sessionID].append(
                                (Arg[1], self.user_email[Arg[1]]))
                            servmsg = f"Welcome, {Arg[1]}."
                        else:
                            servmsg = "Login failed."
                    else:
                        servmsg = "Login failed."
            lock.release()
        elif cmd == "logout":
            lock.acquire()
            if len(Arg) != 1:
                servmsg = 'Usage: logout'
            else:
                if len(self.Session[sessionID]) == 0:
                    servmsg = "Please login first."
                else:
                    flag = 0
                    for k,v in self.chatroom_info.items():
                        if v.creator == self.Session[sessionID][-1][0]:
                            if v.status == "open":
                                flag = 1
                                servmsg = "Please do attach and leave-chatroom first."
                                break
                    if flag == 0:
                        LastLogin = self.Session[sessionID].pop()
                        servmsg = f"Bye, {LastLogin[0]}."
            lock.release()
        elif cmd == "list-user":
            servmsg = 'Name\tEmail'
            for k, v in self.user_email.items():
                servmsg += '\n' + k + '\t' + v
        elif cmd == "whoami":
            if len(Arg) != 1:
                servmsg = 'Usage: whoami'
            else:
                if len(self.Session[sessionID]) == 0:
                    servmsg = "Please login first."
                else:
                    servmsg = self.Session[sessionID][-1][0]
        elif cmd == "create-board":
            lock.acquire()
            if len(Arg) != 2:
                servmsg = 'Usage: create-board <name>'
            else:
                if len(self.Session[sessionID]) == 0:
                    servmsg = "Please login first."
                else:
                    flag = 0
                    for k,v in self.board_info.items():
                        if v.name == Arg[1]:
                            flag = 1
                    if flag == 1:
                        servmsg = "Board already exists"
                    else:
                        board = Board()
                        board.moderator = self.Session[sessionID][-1][0]
                        board.name = Arg[1]
                        self.bd += 1
                        self.board_info[self.bd] = board
                        servmsg = "Create board successfully."
            lock.release()
        elif cmd == "create-post":
            lock.acquire()
            if len(Arg) < 6:
                servmsg = "Usage: create-post <board-name> --title <title> --content <content>"
            elif len(self.Session[sessionID]) == 0:
                servmsg = "Please login first." 
            else:
                flag = 0
                for k,v in self.board_info.items():
                    if v.name == Arg[1]:
                        post = Post()
                        post.author = self.Session[sessionID][-1][0]
                        x = Arg.index("--title")
                        y = Arg.index("--content")
                        for i in range(len(Arg)):
                            if i > x and i < y:
                                post.title += Arg[i]
                                post.title += " "
                            elif i > y:
                                post.content += Arg[i]
                                post.content += " "
                        post.content = post.content.replace("<br>", "\n")
                        t = time.time()
                        t = time.localtime(t)
                        post.date = time.asctime(t)
                        self.sn += 1
                        self.post_info[self.sn] = post
                        self.board_info[k].post_ids.append(self.sn)
                        servmsg = "Create post successfully."
                        flag = 1
                if flag == 0:
                    servmsg = "Board does not exist."
            lock.release()
        elif cmd == "list-board":
            lock.acquire()
            servmsg = "Index\tName\tModerator"
            for k,v in self.board_info.items():
                servmsg += '\n' + str(k) + '\t' + v.name + '\t' + v.moderator
            lock.release()
        elif cmd == "list-post":
            lock.acquire()
            if len(Arg) != 2:
                servmsg = "Usage: list-post <board-name>"
            else:
                flag = 0
                for k,v in self.board_info.items():
                    if v.name == Arg[1]:
                        flag = 1
                        servmsg = "S/N\tTitle\tAuthor\tDate"
                        if len(v.post_ids) == 0:
                            break
                        else:
                            for i in self.board_info[k].post_ids:
                                servmsg += "\n" + str(i) + "\t" + self.post_info[i].title + "\t"
                                servmsg += self.post_info[i].author + "\t" + self.post_info[i].date
                if flag == 0:
                    servmsg = "Board does not exist."
            lock.release()
        elif cmd == "read":
            lock.acquire()
            if len(Arg) != 2:
                servmsg = "Usage: read <post-S/N>"
            elif self.post_info.get(int(Arg[1])) == None:
                servmsg = "Post does not exist."
            else:
                servmsg += "Author: " + self.post_info[int(Arg[1])].author + "\n"
                servmsg += "Title: " + self.post_info[int(Arg[1])].title + "\n"
                servmsg += "Date: " + self.post_info[int(Arg[1])].date + "\n"
                servmsg += "--\n"
                servmsg += self.post_info[int(Arg[1])].content + "\n--"
                for i in self.post_info[int(Arg[1])].comment:
                    servmsg += '\n' + self.comment_info[i].author + ': '
                    servmsg += self.comment_info[i].content
            lock.release()
        elif cmd == "delete-post":
            lock.acquire()
            if len(Arg) != 2:
                servmsg = "Usage: delete-post <post-S/N>"
            elif len(self.Session[sessionID]) == 0:
                servmsg = "Please login first." 
            elif self.post_info.get(int(Arg[1])) == None:
                servmsg = "Post does not exist."
            elif self.Session[sessionID][-1][0] != self.post_info[int(Arg[1])].author:
                servmsg = "Not the post owner."
            else: 
                for k,v in self.board_info.items():
                    if int(Arg[1]) in v.post_ids:
                        v.post_ids.remove(int(Arg[1]))
                self.post_info.pop(int(Arg[1]))
                servmsg = "Delete successfully."
            lock.release()
        elif cmd == "update-post":
            lock.acquire()
            if len(Arg) < 4:
                servmsg = "Usage: update-post <post-S/N> --title/content <new>" 
            elif len(self.Session[sessionID]) == 0:
                servmsg = "Please login first." 
            elif self.post_info.get(int(Arg[1])) == None:
                servmsg = "Post does not exist."
            elif self.Session[sessionID][-1][0] != self.post_info[int(Arg[1])].author:
                servmsg = "Not the post owner."
            else:
                if Arg[2] == "--title":
                    self.post_info[int(Arg[1])].title = ""
                    for i in range(len(Arg)):
                        if i > 2:
                            self.post_info[int(Arg[1])].title += Arg[i] + " "
                else:
                    self.post_info[int(Arg[1])].content = ""
                    for i in range(len(Arg)):
                        if i > 2:
                            self.post_info[int(Arg[1])].content += Arg[i] + " "
                    self.post_info[int(Arg[1])].content = self.post_info[int(Arg[1])].content.replace("<br>", "\n")
                servmsg = "Update successfully."
            lock.release()
        elif cmd == "comment":
            lock.acquire()
            if len(Arg) < 3:
                servmsg = "Usage: comment <post-S/N> <comment>"
            elif len(self.Session[sessionID]) == 0:
                servmsg = "Please login first." 
            elif self.post_info.get(int(Arg[1])) == None:
                servmsg = "Post does not exist."
            else:
                comment = Comment()
                comment.author = self.Session[sessionID][-1][0]
                for i in range(len(Arg)):
                    if i > 1:
                        comment.content += Arg[i] + " "
                self.cm += 1
                self.comment_info[self.cm] = comment
                self.post_info[int(Arg[1])].comment.append(self.cm)
                servmsg = "Comment successfully."
            lock.release()
        elif cmd == "create-chatroom":
            lock.acquire()
            if len(Arg) < 2:
                servmsg = "Usage: create-chatroom <port>"
            elif len(self.Session[sessionID]) == 0:
                servmsg = "Please login first."
            else:
                flag = 0
                for k,v in self.chatroom_info.items():
                    if v.creator == self.Session[sessionID][-1][0]:
                        servmsg = "User has already created the chatroom."
                        flag = 1
                        break
                if flag == 0:
                    chatroom = Chatroom()
                    chatroom.creator = self.Session[sessionID][-1][0]
                    chatroom.status = "open"
                    chatroom.port = int(Arg[1])
                    self.cr += 1
                    self.chatroom_info[self.cr] = chatroom
                    servmsg = "start to create chatroom..."
            lock.release()
        elif cmd == "list-chatroom":
            if len(self.Session[sessionID]) == 0:
                servmsg = "Please login first."
            else:
                servmsg = "Chatroom_name\tStatus"
                for k,v in self.chatroom_info.items():
                    servmsg += "\n" + v.creator + "\t" + v.status
        elif cmd == "join-chatroom":
            lock.acquire()
            if len(Arg) < 2:
                servmsg = "Usage: join-chatroom <chatroom_name>" 
            elif len(self.Session[sessionID]) == 0:
                servmsg = "Please login first."
            else:
                flag = 0
                for k,v in self.chatroom_info.items():
                    if v.creator == Arg[1]:
                        if v.status == "close":
                            servmsg = "The chatroom does not exist or the chatroom is close."
                        else:
                            flag = 1
                            port = v.port
                        break
                if flag == 0:
                    servmsg = "The chatroom does not exist or the chatroom is close."
                else:
                    servmsg = "join " + str(port)
            lock.release()
        elif cmd == "attach":
            lock.acquire()
            if len(self.Session[sessionID]) == 0:
                servmsg = "Please login first."
            else:
                flag = 0
                for k,v in self.chatroom_info.items():
                    if v.creator == self.Session[sessionID][-1][0]:
                        flag = 1
                        servmsg = "attach"
                        break
                if flag == 0:
                    servmsg = "Please create-chatroom first."
            lock.release()
        elif cmd == "restart-chatroom":
            lock.acquire()
            if len(self.Session[sessionID]) == 0:
                servmsg = "Please login first."
            else:
                flag = 0
                for k,v in self.chatroom_info.items():
                    if v.creator == self.Session[sessionID][-1][0]:
                        flag = 1
                        if v.status == "open":
                            servmsg = "Your chatroom is still running."
                        else:
                            v.status = "open"
                            servmsg = "start to create chatroom..."
                        break
                if flag == 0:
                    servmsg = "Please create-chatroom first."
            lock.release()
        elif cmd == "leave-chatroom":
            lock.acquire()
            for k,v in self.chatroom_info.items():
                if v.creator == self.Session[sessionID][-1][0]:
                    v.status = "close"
                    break
            lock.release()
        elif cmd == "exit":
            self.Session[sessionID] = None
            sessionID = -1
        else:
            servmsg = f"{cmd}: Command not found!"
        return json.dumps({"msg": servmsg, "sid": sessionID})

def main():
    if len(sys.argv) != 2:
        print(f"\tUsage {sys.argv[0]} <Port>")
        exit(-1)
    HOSTNAME, ListenPort = "", int(sys.argv[1])
    server = ServerService()
    TCPsockfd = socket(AF_INET, SOCK_STREAM)
    TCPsockfd.bind((HOSTNAME, ListenPort))
    TCPsockfd.listen(10)
    UDPsockfd = socket(AF_INET, SOCK_DGRAM)
    UDPsockfd.bind((HOSTNAME, ListenPort))
    inputs = [TCPsockfd, UDPsockfd]
    try:
        while True:
            readable, writable, exceptional = select(inputs, [], [], 0)
            for sockfd in readable:
                if sockfd == TCPsockfd:
                    connfd, addr = sockfd.accept()
                    t = threading.Thread(target = server.HandleTCP, args = (connfd, addr))
                    t.daemon = True
                    t.start()
                elif sockfd == UDPsockfd:
                    t = threading.Thread(target = server.HandleUDP, args = (sockfd, ))
                    t.daemon = True
                    t.start()
                else:
                    print(f"Unknown type of socket: {sockfd}")
    except KeyboardInterrupt:
        print("\nServer close.")
    for sockfd in inputs:
        sockfd.close()


if __name__ == "__main__":
    main()
