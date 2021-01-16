#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <unistd.h>
using namespace std;

const int MAX_LEN = 2048;   
char buf[MAX_LEN];
int port;
int TCP_sockfd, UDP_sockfd, ut; 
struct sockaddr_in server_addr;

int create_socket_TCP(string, int);
int create_socket_UDP(string, int);
void send_to_server(string);
void read_from_server();
void get_port();

int main(int argc, char* argv[]){
    if(argc < 3){
        printf("Usage: client [ip] [port]\n");
        exit(EXIT_FAILURE);
    }
    TCP_sockfd = create_socket_TCP(string(argv[1]), atoi(argv[2]));
    UDP_sockfd = create_socket_UDP(string(argv[1]), atoi(argv[2]));
    read_from_server();
    char msg[] = "port";
    int addr_len = sizeof(struct sockaddr_storage);
    sendto(UDP_sockfd, msg, strlen(msg), 0, (struct sockaddr *)&server_addr, addr_len);
    get_port();
    read_from_server();
    while(1){
        string input;
        getline(cin, input);
        send_to_server(input);
        if(input == "exit") break;
        read_from_server();
    }
    close(UDP_sockfd);
}

int create_socket_TCP(string ip, int port){
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    bzero(&server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET; //IPv4
    server_addr.sin_addr.s_addr = inet_addr(ip.c_str());
    server_addr.sin_port = htons(port);

    int optval = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const void *) &optval, sizeof(int)) == -1) {
        printf("Error: setsockopt() failed\n");
        exit(EXIT_FAILURE);
    }
    
    if (connect(sockfd, (struct sockaddr *) &server_addr, sizeof(server_addr)) < 0)  {
        printf("Error: connect() failed\n");
        exit(EXIT_FAILURE);
    }
    return sockfd;
}

int create_socket_UDP(string ip, int port){
    //struct sockaddr_in server_addr;
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    bzero(&server_addr, sizeof(server_addr));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(ip.c_str());
    server_addr.sin_port = htons(port);

    int optval = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const void *) &optval, sizeof(int)) == -1) {
        printf("Error: setsockopt() failed\n");
        exit(EXIT_FAILURE);
    }
    return sockfd;
}

void send_to_server(string message){
    int addr_len = sizeof(struct sockaddr_storage);
    message += " ";
    message += to_string(port);
    message += "\n";
    char msg[message.length() + 5];
    sprintf(msg, "%s", message.c_str());

    if(message[0] == 'r' || message[0] == 'w')
        ut = 1;
    else
        ut = 0;
    
    if(ut)
        sendto(UDP_sockfd, msg, strlen(msg), 0, (struct sockaddr*) &server_addr, addr_len);
    else        
        send(TCP_sockfd, msg, strlen(msg), 0);
    cout << TCP_sockfd;
}

void read_from_server(){
    memset(buf, 0, sizeof(buf));
    int n;
    socklen_t addr_len = sizeof(struct sockaddr_storage);

    if(ut) 
        n = recvfrom(UDP_sockfd, buf, MAX_LEN, 0, (struct sockaddr*) &server_addr, &addr_len);
    else{
        n = recv(TCP_sockfd, buf, MAX_LEN, 0);
    }        

    
    string response = string(buf);
    cout << response << flush;
}

void get_port() {
    memset(buf, 0, sizeof(buf));
    socklen_t addr_len = sizeof(struct sockaddr_storage);
    recvfrom(UDP_sockfd, buf, MAX_LEN, 0, (struct sockaddr*) &server_addr, &addr_len);
    string str = string(buf);
    for (int i = 0; str[i] != '\n'; ++i){
        port = port * 10 + (int)(str[i] - '0');
    }
}