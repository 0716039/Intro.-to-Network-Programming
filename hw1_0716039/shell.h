#pragma once

#include <iostream>
#include <cstdlib>
#include <vector>
#include <map>
#include <unistd.h>
#include "client.h"
#include "user.h"

using namespace std;

extern map<int, string> clients;
extern int current_sockfd;

void remove_space(string& str) {
    while (str.length() > 0 && str.at(0) == ' ') str.erase(0, 1);
}

string split(string& str, string delim) {
    int pos = str.find(delim);
    string res = str.substr(0, pos);
    str.erase(0, pos);
    return res;
}

vector<string> parse(string input) {
    vector<string> args;
    args.clear();
    while (input.length() > 0) {
        remove_space(input);
        if (input.length() == 0)    break;

        string arg = split(input, " ");
        args.push_back(arg);
    }
    return args;
}

string execute(string input) {
    string response = "";
    // clear '\r' added by telnet
    if (input.back() == '\r')   input.pop_back();

    remove_space(input);
    string cmd_name = split(input, " ");
    vector<string> args = parse(input);

    if (cmd_name == "register") {
        response = execute_register(args);
    }
    if (cmd_name == "login") {
        response = execute_login(args);
    }
    if (cmd_name == "logout") {
        response = execute_logout(args);
    }
    if (cmd_name == "whoami") {
        response = execute_whoami(args);
    }
    if (cmd_name == "list-user"){
        response = execute_listuser();
    }
    if (cmd_name == "exit") {
        response = execute_exit();
    }
    return response;
}