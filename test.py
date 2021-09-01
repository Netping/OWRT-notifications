#!/usr/bin/python3

from notify import *


def handle_event(event, data):
    print(event)
    print(data)

def main():
    n = notificator()

    n.applyconfig()

if __name__ == "__main__":
    main()
