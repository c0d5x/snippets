#!/usr/bin/env python

from random import random
from clock import clock
from time import sleep


@clock
def sleeper(interval=0):
    if interval == 0:
        interval = int(random() * 2)
    sleep(interval)

if __name__ == "__main__":
    sleeper()
    sleeper(1)
    sleeper(2)
    sleeper(interval=4)
    sleeper()
