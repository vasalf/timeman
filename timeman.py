#!/usr/bin/pypy3

#--Get the full dat file name
from subprocess import check_output
datname = "/home/" + check_output("whoami").decode("utf-8").rstrip() + "/.local/timeman.dat"

import fractions, datetime


#--Open dat file and return all tasks
def parse_dat():
    dat = open(datname, "r")
    s = dat.readline().rstrip()
    res = []
    while s != "":
        s_id, dl, s_a, s_b = s.split()
        name = dat.readline().rstrip()
        desc = dat.readline().rstrip()
        iid = int(s_id)
        day, month, year = map(int, dl.split('.'))
        deadline = datetime.date(year, month, day)
        a, b = map(int, [s_a, s_b])
        s = dat.readline().rstrip()
        status = fractions.Fraction(a, b)
        res.append((iid, name, deadline, status, desc))
    dat.close()
    return res


#--Get a status and return a status bar
def status_str(frac):
    res = "["
    for i in range(10):
        if frac * 100 >= 10 * (i + 1):
            res += "#"
        else:
            res += "-"
    res += "] " + str(int(float(frac * 100))) + "%"
    return res.ljust(17)


#--Get a date and return a string
def date_str(d):
    return "%02d.%02d.%04d" % (d.day, d.month, d.year)


#--Open dat file and write changes
def write_dat(tasks):
    dat = open(datname, "w")
    for iid, name, dl, status, desc in tasks:
        dat.write(str(iid) + " " + date_str(dl) + " " + str(status.numerator) + " " + str(status.denominator) + "\n")
        dat.write(name + "\n")
        dat.write(desc + "\n")


#--This code parses command line arguments.
import argparse
parser = argparse.ArgumentParser(prog="timeman", description="A simple organizer")
subparsers = parser.add_subparsers(help="What do you want to do", dest="command")
#--Parse add command
add_cmd_parser = subparsers.add_parser("add", help="Add a task")
add_cmd_parser.add_argument("--forse-id", type=int, help="Forse set a task ID. WARNING: It may be dangerous")
#--Parse show command
show_cmd_parser = subparsers.add_parser("show", help="Show all tasks")
show_cmd_parser.add_argument("-c", "--closest", type=int, help="Show only that number of tasks")
show_cmd_parser.add_argument("--no-late", action="store_true", help="Don't show late tasks")
show_cmd_parser.add_argument("--done", action="store_true", help="Show even done tasks")
#--Parse show-task command
show_task_cmd_parser = subparsers.add_parser("show-task", help="Show particular task")
show_task_cmd_parser.add_argument("ID", type=int, help="Task ID")
show_task_cmd_parser.add_argument("--done", action="store_true", help="Dhow even done tasks")
#--Parse set command
set_cmd_parser = subparsers.add_parser("set", help="Set task status")
set_cmd_parser.add_argument("ID", type=int, help="Task ID")
set_cmd_parser.add_argument("NUM", type=int, help="Fraction numerator")
set_cmd_parser.add_argument("DENOM", type=int, help="Fraction denominator")
#--Parse make command
make_cmd_parser = subparsers.add_parser("make", help="Make tasks file")
args = parser.parse_args()

#--Now we can run commands
if args.command == "make":
#--Run make command
    print("WARNING: You will lose all your tasks")
    print("Do you want to continue?(yes/no):", end=" ")
    ans = input().rstrip()
    if ans == "yes":
        from os import system
        system("rm ~/.local/timeman.dat > /dev/null")
        system("touch ~/.local/timeman.dat")
    else:
        print("Aborting")
elif args.command == "show":
#--Run show command
    if args.closest == None:
        last = 10 ** 6
    else:
        last = args.closest
    tasks = parse_dat()
    to_show = []
    for iid, name, dl, status, desc in tasks:
        if status != 1 or args.done:
            if not args.no_late or dl >= datetime.date.today():
                to_show.append((iid, name, dl, status, desc))
    to_show.sort(key=lambda x : x[2])
    if (len(to_show)):
        print("+" + "-" * 8 + "+" + "-" * 12 + "+" + "-" * 19 + "+" + "-" * 17 + "+")
        print("| " + " | ".join(["ID".ljust(6), "Deadline".ljust(10), "Progress".ljust(17), "Name".ljust(15)]) + " |")
        print("+" + "-" * 8 + "+" + "-" * 12 + "+" + "-" * 19 + "+" + "-" * 17 + "+")
        for iid, name, dl, status, desc in to_show:
            if last > 0:
                from os import system
                if dl < datetime.date.today() and status != 1:
                    system("tput setaf 1")
                print( "| " + " | ".join(map(str, [str(iid).rjust(6), date_str(dl), status_str(status), name.ljust(15)])) + " |")
                last -= 1
                if dl < datetime.date.today() and status != 1:
                    system("tput sgr0")
        print("+" + "-" * 8 + "+" + "-" * 12 + "+" + "-" * 19 + "+" + "-" * 17 + "+")
elif args.command == "show-task":
#--Run show-task command
    tasks = parse_dat()
    for iid, name, dl, status, desc in tasks:
        if iid == args.ID and (args.done or status != 1):
            print()
            print("ID:".ljust(13), iid)
            print("Name:".ljust(13), name)
            print("Deadline:".ljust(13), date_str(dl))
            print("Status:".ljust(13), status_str(status))
            print("Description:".ljust(13), desc)
elif args.command == "set":
#--Run set command
    tasks = parse_dat()
    for i in range(len(tasks)):
        if tasks[i][0] == args.ID:
            iid, name, dl, status, desc = tasks[i]
            tasks[i] = iid, name, dl, fractions.Fraction(args.NUM, args.DENOM), desc
    write_dat(tasks)
elif args.command == "add":
#--Run add command
    tasks = parse_dat()
    if args.forse_id:
        t_id = args.forse_id
    else:
        t_id = 0
        for iid, name, dl, status, desc in tasks:
            t_id = max(t_id, iid)
        t_id += 1
    print("Print task name:")
    name = input()
    assert(len(name) <= 15)
    print("Print task deadline in format DD.MM.YYY:")
    d, m, y = map(int, input().split("."))
    dl = datetime.date(y, m, d)
    print("Print task description:")
    desc = input()
    tasks.append((t_id, name, dl, fractions.Fraction(0), desc))
    write_dat(tasks)
    print("OK, task ID is", t_id)
