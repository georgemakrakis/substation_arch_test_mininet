#!/bin/bash

# The -E option preserves the env variables for the user. Is is necessary to run GUI apps like wireshark.
sudo -E mn --controller=remote,ip=127.0.0.1 --mac --switch ovsk,protocols=OpenFlow13 -i 10.1.1.0/24 --topo single,3