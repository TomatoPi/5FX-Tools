#!/usr/bin/python

import json
import requests
import subprocess as sp

class FailedCommand (Exception) :
    pass

def set_port_property(port, prop, value, type) :

    proc = sp.run(['jack_property', '-p', '-s', port, prop, value], stdout=sp.PIPE)
    if proc.returncode != 0 :
        raise FailedCommand(proc)


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

    blob = json.loads(GET(URL))
    
    datastore = dict()

    for key in blob :
        path = key.split('/')
        
        itr = datastore

        for i in range(len(path)-1) :
            item = path[i]
            if item not in itr :
                itr[item] = dict()
            itr = itr[item]
        itr[path[-1]] = blob[key]
        
    # print(datastore)

    return datastore

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

    computer_io_candidates = list(filter(lambda x : x[1]['name'].find('Computer') != -1, banks.items()))
    if 1 != len(computer_io_candidates) :
        raise RuntimeError("Failed retrieve computer bank index")
    
    computer_index = computer_io_candidates[0][0]
    computer_bank = computer_io_candidates[0][1]
    # print(computer_bank)

    channels = computer_bank['ch']
    active_channels_count = int(computer_bank['calcCh'])
    # print(channels)

    names_dict = {chan : channels[chan]['name'] for chan in channels}
    names = [names_dict[str(i)] for i in range(active_channels_count)]
    print(names)

    # Set appropriate JACK Metadatas to system ports

    for idx, name in enumerate(names) :
        
        port = f"{portbase}{idx+1}"
        sp.run(f'jack_property -p -d {port} http://jackaudio.org/metadata/pretty-name'.split(' '))

        if 0 == len(name) :
            name = f"_{idx+1}"
        set_port_property(port, 'http://jackaudio.org/metadata/pretty-name', name, 'text/plain')
        # set_port_property(port, 'http://jackaudio.org/metadata/hardware', name, 'text/plain')

    # done

if __name__ == '__main__' :

    IP = "192.168.1.16"

    configure_pretty_names(IP, 'i')
    configure_pretty_names(IP, 'o')