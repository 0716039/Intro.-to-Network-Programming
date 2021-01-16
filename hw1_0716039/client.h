#pragma once

#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <sys/types.h>
#include <unistd.h>

using namespace std;

map<int, string> clients, clients_port;
int current_sockfd, current_port;
int TCPserver_sockfd, UDPserver_sockfd;
fd_set allset, rset;


void init_clients() {
    clients.clear();
    clients_port.clear();
}

void add_client(int sockfd) {
    clients[sockfd] = "";
}

void add_client_port(int port) {
    clients_port[port] = "";
}

void remove_client() { 
    dup2(TCPserver_sockfd, fileno(stdin));
    clients.erase(current_sockfd);
    clients_port.erase(current_port);
    FD_CLR(current_sockfd, &allset);
    close(current_sockfd);
}
