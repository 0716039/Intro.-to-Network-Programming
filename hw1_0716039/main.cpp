#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <unistd.h>
#include "client.h"
#include "shell.h"

using namespace std;

extern map<int, string> clients, clients_port;
extern int current_sockfd, current_port;
extern int TCPserver_sockfd, UDPserver_sockfd;
extern fd_set allset, rset;

int create_socket_TCP(int, int);
int create_socket_UDP(int, int);
void handle_new_connection(int);
void handle_old_connection(int);


const int MAX_LEN = 2048;
char buf[MAX_LEN];
struct sockaddr_in server_addr;

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: ./server [port]\n");
        exit(EXIT_FAILURE);
    }
    
    TCPserver_sockfd = create_socket_TCP(atoi(argv[1]), 30);
    UDPserver_sockfd = create_socket_UDP(atoi(argv[1]), 30);

    int max_fd = TCPserver_sockfd + UDPserver_sockfd;
    struct timeval tv;

    tv.tv_sec = 3;
    tv.tv_usec = 0;

    FD_ZERO(&allset);
    FD_SET(TCPserver_sockfd, &allset);
    FD_SET(UDPserver_sockfd, &allset);

    init_clients();

    while (true) {
        rset = allset;
        while (select(max_fd + 1, &rset, NULL, NULL, &tv) < 0);
        
        if (FD_ISSET(TCPserver_sockfd, &rset)) {
            struct sockaddr_in client_addr;
            socklen_t client_addr_len = sizeof(client_addr);
            int client_sockfd;
            while ((client_sockfd = accept(TCPserver_sockfd, (struct sockaddr*) &client_addr, &client_addr_len)) < 0);

            FD_SET(client_sockfd, &allset);
            max_fd = max(max_fd, client_sockfd + UDPserver_sockfd);
            handle_new_connection(client_sockfd);
        }

        map<int, string>::iterator it;
        for (it = clients.begin(); it != clients.end(); it++) {
            int sockfd = it->first;
            if (!FD_ISSET(sockfd, &rset))   continue;
            handle_old_connection(sockfd);
        }
        
        if (FD_ISSET(UDPserver_sockfd, &rset)) {
            struct sockaddr_in client_addr;
            socklen_t client_addr_len = sizeof(struct sockaddr_storage);
            memset(buf, 0, sizeof(buf));
            recvfrom(UDPserver_sockfd, buf, MAX_LEN, 0, (struct sockaddr *)&client_addr, &client_addr_len);
            string response = string(buf);
        
            if(response[0] == 'p'){
                int client_addr_len = sizeof(struct sockaddr_storage);
                add_client_port(client_addr.sin_port);
                string str = to_string(client_addr.sin_port);
                str += "\n";
                char msg[str.length() + 5];
                sprintf(msg, "%s", str.c_str());
                sendto(UDPserver_sockfd, msg, strlen(msg), 0, (struct sockaddr*) &client_addr, client_addr_len);
            }
            else{
                int client_addr_len = sizeof(struct sockaddr_storage);
                string output = execute(response);
                output += "% ";
                char msg[output.length() + 5];
                sprintf(msg, "%s", output.c_str());
                sendto(UDPserver_sockfd, msg, strlen(msg), 0, (struct sockaddr *)&client_addr, client_addr_len);
                write(UDPserver_sockfd, "% ", strlen("% "));
            }
        }
        
    }
    return 0;
}

int create_socket_TCP(int port, int listenQ) {
    //struct sockaddr_in server_addr;
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    bzero(&server_addr, sizeof(server_addr));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    int optval = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const void *) &optval, sizeof(int)) == -1) {
        printf("Error: setsockopt() failed\n");
        exit(EXIT_FAILURE);
    }

    if (bind(sockfd, (struct sockaddr*) &server_addr, sizeof(server_addr)) < 0) {
        printf("Error: bind() failed\n");
        exit(EXIT_FAILURE);
    }

    if (listen(sockfd, listenQ) < 0) {
        printf("Error: listen() failed\n");
        exit(EXIT_FAILURE);
    }
    return sockfd;
}

int create_socket_UDP(int port, int listenQ) {
    //struct sockaddr_in server_addr;
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    bzero(&server_addr, sizeof(server_addr));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    int optval = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const void *) &optval, sizeof(int)) == -1) {
        printf("Error: setsockopt() failed\n");
        exit(EXIT_FAILURE);
    }

    if (bind(sockfd, (struct sockaddr*) &server_addr, sizeof(server_addr)) < 0) {
        printf("Error: bind() failed\n");
        exit(EXIT_FAILURE);
    }
    
    return sockfd;
}

void handle_new_connection(int sockfd) {
    printf("New connection.\n");

    char msg[] = "********************************\n"
                 "** Welcome to the BBS server. **\n"
                 "********************************\n";
    write(sockfd, msg, strlen(msg));
    add_client(sockfd);
    write(sockfd, "% ", strlen("% "));
}

void handle_old_connection(int sockfd) {
    dup2(sockfd, fileno(stdin));
    current_sockfd = sockfd;

    cout << sockfd;
    string input;
    getline(cin, input);
    string output = execute(input);
    output += "% ";
    char msg[output.length() + 5];
    sprintf(msg, "%s", output.c_str());
    write(sockfd, msg, strlen(msg));
}