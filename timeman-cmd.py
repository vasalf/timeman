#!/usr/bin/pypy3

from os import system

while True:
    system("clear")
    system("cal --three --monday")
    system("timeman show")
    while True:
        print()
        print("> ", end="")
        s = input()
        arr = s.split()
        if arr[0] == "update":
            break
        if arr[0] == "help":
            system("timeman --help")
            continue
        if arr[0][:4] == "show":
            system("timeman " + s)
            continue
        system("timeman " + s)
        break
