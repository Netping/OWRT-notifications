#!/usr/bin/python3

from notify import *


def main():
    n = notificator()

    n.applyconfig()
    print("Waiting...")

if __name__ == "__main__":
    main()
