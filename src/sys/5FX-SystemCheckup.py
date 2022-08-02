#!/usr/bin/python

import os
import sys
import re
import subprocess as sp
import lark

class FailedCommand (Exception) :
    pass

class MissingDevice (Exception) :
    pass

class FailedTest (Exception) :
    pass

def run(command) :
    proc = sp.run(command.split(' '), stdout=sp.PIPE)
    output = proc.stdout.decode()
    return output

def check_devices(devices) : 
    # print("""Checking devices status ... """, end='')
    proc = sp.run('cat /proc/asound/cards'.split(' '), stdout=sp.PIPE)
    output = proc.stdout.decode()
    if proc.returncode != 0 :
        raise FailedCommand(f"{proc}")

    # regex = re.compile(r'^.* (\w*) -> card(\d+)$', re.MULTILINE) # ls -l /proc/asound
    regex = re.compile(r'(\d)+\s*\[(\w+)\s*\]:\s*(\w[^\n]*)\s*(\w[^\n]*)') # cat /proc/asound/cards
    matches = regex.findall(output)
    # print(matches)

    result = {item[1] : (item[0], item[2:]) for item in matches}
    print(result)

    missing_devs = []

    for dev in devices :
        if dev not in result :
            missing_devs.append(dev)

    if 0 < len(missing_devs) :
        raise MissingDevice(f"{missing_devs}")
    
    # print("""Ok""")
    return result

def check_system_realtime(devices, card) :

    desc = devices[card]
    
    regex = re.compile(r'.*usb-\d+:(\d{2}:\d{2}\.\d).*')
    matches = regex.findall(desc[1][1])
    # print(matches)

    bus = matches[0]

    output = run('lspci -vvv')
    # print(output)
    
    output = output.split('\n\n')
    # for x in output :
    #     print("==")
    #     print(x)
    #     print("--")
    
    # print("*************")

    output = {item[0:7] : item[8:] for item in output}
    # for x in output :
    #     print("==")
    #     print(f"'{x}' : '''{output[x]}'''")
    #     print("--")

    regex = re.compile(r'^[ \t]*(\w+[\w ]*) *: *(.*)$', re.MULTILINE)
    matches = regex.findall(output[bus])
    # print(bus, output[bus], matches)

    properties = {item[0] : item[1] for item in matches}
    # print(properties)

    blob = properties['Interrupt']
    regex = re.compile(r'.*IRQ (\d+).*')
    
    irq = regex.match(blob).group(1)
    os.environ['SOUND_CARD_IRQ'] = irq
    # print(irq)

    proc = sp.run('realTimeConfigQuickScan', stdout=sp.PIPE, env=os.environ)
    output = proc.stdout.decode()
    # print(output)

    fail = False
    failed_tests = []
    for line in output.split('\n') :
        if '\x1b[1m\x1b[31mnot good\x1b[0m' in line or 'not ok.' in line or line.startswith('**') :
            fail = True
            failed_tests.append(['-'.join(line.split('-')[:-1])])
        elif fail :
            if '\x1b[1m\x1b[32mgood\x1b[0m' in line or 'ok.' in line :
                fail = False
            else :
                failed_tests[-1].append(line)
    
    result = {item[0] : '\n'.join(item[1:]) for item in failed_tests}
    if 0 < len(failed_tests) :
        raise FailedTest(f"{failed_tests}")

if __name__ == '__main__' :
    DEVICES = sys.argv[1:]
    if 0 == len(DEVICES) :
        DEVICES = ["D5FXInterface", "O88", "S49"]

    devices = check_devices(DEVICES)
    check_system_realtime(devices, DEVICES[0])


