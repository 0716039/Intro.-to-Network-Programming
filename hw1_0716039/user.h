#pragma once

#include <iostream>
#include <vector>
#include <map>
#include "client.h"
using namespace std;

struct User {
    string email;
    string password;
    
    User(string email = "", string password = "") : email(email), password(password) {}
};

map<string, User> users; 


string execute_register(const vector<string> &args) {
    string response;
    if (args.size() != 4) {
        response = "Usage: register <username> <email> <password>\n";
        return response;
    }
    string username = args.at(0);
    string email = args.at(1);
    string password = args.at(2);
    if (users.find(username) != users.end()) {
        response = "Username is already used.\n";
        return response;
    }
    users[username] = User(email, password);
    response = "Register successfully.\n";
    return response;
}

string execute_login(const vector<string> &args) {
    string response;
    if (args.size() != 3) {
        response = "Usage: login <username> <password>\n";
        return response;
    }
    
    current_port = (stoi)(args.at(2));
    string current_username = clients_port[current_port];
    string username = args.at(0);
    string password = args.at(1);

    if (current_username != "") {
        response = "Please logout first.\n";
        return response;
    }
    if (users.find(username) == users.end()) {
        response = "Login failed.\n";
        return response;
    }
    if (users[username].password != password) {
        response = "Login failed.\n";
        return response;
    }
    clients_port[current_port] = username;
    response += "Welcome, ";
    response += username;
    response += ".\n";
    return response;
}

string execute_logout(const vector<string> &args) {
    string response;
    current_port = (stoi)(args.at(0));
    string current_username = clients_port[current_port];
    if (current_username == "") {
        response = "Please login first.\n";
        return response;
    }
    clients_port[current_port] = "";
    response += "Bye, ";
    response += current_username;
    response += ".\n";
    return response;
}

string execute_whoami(const vector<string> &args) {
    string response;
    current_port = (stoi)(args.at(0));
    string current_username = clients_port[current_port];
    if (current_username == "") {
        response = "Please login first.\n";
        return response;
    }
    response += current_username;
    response += "\n";
    return response;
}
string execute_listuser() {
    string response;
    response = "Name      Email\n";
    map<string, User>::iterator iter;
    for (iter = users.begin(); iter != users.end(); iter++){
        response += iter->first;
        response += "        ";
        response += iter->second.email;
        response += "\n";
    }
    return response;
}
string execute_exit() {
    string response = "\n";
    remove_client();
    return response;
}