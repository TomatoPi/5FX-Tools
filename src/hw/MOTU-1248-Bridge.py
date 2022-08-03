#!/usr/bin/python

import json
import requests
import subprocess as sp

class FailedCommand (Exception) :
    pass

def run(command, output = True) :
    proc = sp.run(command.split(' '), stdout=sp.PIPE)
    if proc.returncode != 0 :
        raise FailedCommand(proc)
    if output :
        return proc.stdout.decode()


def GET(url, timeout=1) :
    
    result = requests.get(url, timeout=timeout)
    if result.status_code != 200 :
        raise RuntimeError(f"Failed GET request : {result}")
    return result.text

def PUT(url, datas, timeout=1) :

    result = requests.put(url, datas, timeout=timeout)
    if result.status_code != 200 :
        raise RuntimeError(f"failed PUT request : {result}")
    return result.text


def get_banks(ip, io) :

    URL = f"http://{ip}/datastore/ext/{io}/"

    blob = GET(URL)
    result = json.loads(blob)
    # print(result)

    return result

def configure_pretty_names(ip, io) :
    
    # card output is computer input and vice-versa
    if io == 'i' :
        iobank = 'obank'
        portbase = 'system:capture_'
    elif io == 'o' :
        iobank = 'ibank'
        portbase = 'system:playback_'

    # Get list of computer IOs and retrieve their names
    banks = get_banks(ip, iobank)
    print(banks)

    computer_io_index = dict(filter(lambda x : x[1]['name'].find('computer') != -1, banks.items()))
    computer_bank = banks[computer_io_index.keys()[0]]
    print(computer_io_index, computer_bank)

    channels = computer_bank['ch']
    names = {chan : computer_bank[chan]['name'] for chan in channels}
    print(names)

    # Set appropriate JACK Metadatas to system ports

    for idx in names :
        break
        name = names[idx]
        run(f'jack_properties -p -s {portbase}{idx} http://jackaudio.org/metadata/pretty-name "{name}"')

    # done

if __name__ == '__main__' :

    IP = "192.168.9.16"

    configure_pretty_names(IP, 'i')
    configure_pretty_names(IP, 'o')