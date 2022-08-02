#!/usr/bin/python

import os
import sys
import subprocess as sp

class FailedCommand (Exception) :
    pass

def run(command, output = True) :
    proc = sp.run(command.split(' '), stdout=sp.PIPE)
    if proc.returncode != 0 :
        raise FailedCommand(proc)
    if output :
        return proc.stdout.decode()

if __name__ == '__main__' :

    # Open wrappers connected to systems IOs
    DEVICES = sys.argv[1:]

    for dev in DEVICES :        
        output = sp.run(f'5FX-IO {dev}', output = False)
