"""Custom topology for a process bus

Below we should visualize the topology, with something like the following:
             host3
               |
               |
               |
   host1 --- switch --- host2

"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.cli import CLI

class process_bus( Topo ):
    def build( self ):

        # Add hosts and switches
        # TODO: These hosts and switches should have the MAC addresses of
        # the devices that we have in the lab. When trying to put something
        # like: D3:13:1C:1B:76:A0 it does not apply and a random mac addrees 
        # is assigned

        # TODO: Maybe use a better structure instead of an array to have those values? 
        # LIke a tuple of IP and MAC?
        self.TMUs = {
            "tmu1": [],
            "tmu2": [],
            "tmu3": [],
            "tmu4": [],
            "tmu5": []
        }

        self.IEDs = {
            "451_1": [],
            # "387_1": [], # This one has only serial connection to the RTAC
            "451_2": [],
            "351_2": [],
            "351_1": [],
            "487B": [],
            "487E": [],
            "787_2": [],
            "651R_1": [],
            "651R_2":[],
            "RTAC":[],
            # "387_2": [] # This one has only serial connection to the RTAC
        }

        self.IDSs = {
            "IDS_1" : []
        }


        TMUs_keys = list(self.TMUs.keys())
        IEDs_keys = list(self.IEDs.keys())

        switch1 = self.addSwitch( "s1", protocols=["OpenFlow13"] )
        
        # Assign IPs and MACs, add hosts and links

        # NOTE: We remove the TMUs completely since they become point-to-point connections
        # for i in range(len(self.TMUs)):
        #      # +2 to start from .2 address
        #     j = i + 2

        #     if j > 9:
        #         j_str = f"{j}"
        #     else:
        #         j_str = f"0{j}"
            
        #     self.TMUs[TMUs_keys[i]].append(f"192.168.1.{j}/24")
        #     self.TMUs[TMUs_keys[i]].append(f"00:00:00:00:00:{j_str}")

        #     TMU = self.addHost( TMUs_keys[i], ip=self.TMUs[TMUs_keys[i]][0], mac=self.TMUs[TMUs_keys[i]][1] )
        #     self.addLink( TMU, switch1 )
        
        for i in range(len(self.IEDs)):
            # +5 casue we did already setup 5 TMUs in this subnet
            j = i + 7
            
            if j > 9:
                j_str = f"{j}"
            else:
                j_str = f"0{j}"

            self.IEDs[IEDs_keys[i]].append(f"192.168.1.{j}/24")
            self.IEDs[IEDs_keys[i]].append(f"00:00:00:00:00:{j_str}")

            IED = self.addHost( IEDs_keys[i], ip=self.IEDs[IEDs_keys[i]][0], mac=self.IEDs[IEDs_keys[i]][1] )
            self.addLink( IED, switch1 )

        # Assigning IDS as well
        self.IDSs["IDS_1"].append(f"192.168.1.120/24")
        self.IDSs["IDS_1"].append(f"00:00:00:00:11:11")

        IDS = self.addHost( "IDS_1", ip=self.IDSs["IDS_1"][0], mac=self.IDSs["IDS_1"][1] )
        self.addLink( IDS, switch1, port1=20, port2=20 )


# topos = { "process_bus": ( lambda: process_bus() ) }


def main():
    topo = process_bus()
    net = Mininet(topo, build=False, waitConnected=True )
    control = RemoteController('c0', ip='127.0.0.1', port=6633) 
    net.addController(control)
    net.build()
    net.start()

    multicast_mapping = {
        "RTAC" : "01:0c:cd:01:00:01"
    }

    scenario_1_hosts = ["RTAC", "651R_2", "787_2", "451_2"]
    
    hosts = net.hosts
    for host in hosts:
        if host.name in scenario_1_hosts:
            # host.cmd("tcpdump -i {0}-eth0 (ether host 01:0c:cd:01:00:01 or ether host 01:0c:cd:01:00:02 or ether host 01:0c:cd:01:00:03 or ether host 01:0c:cd:01:00:04 or ether host 01:0c:cd:01:00:07 or ether host 01:0c:cd:01:00:08) -w ./exp_1/exp_1_{0}.pcap &".format(host.name))
            host.cmd("tcpdump -i {0}-eth0 -w ./exp_1/exp_1_{0}.pcap &".format(host.name))
            host.cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic/goose_CHE_203_generic {0}-eth0 {0}' &".format(host.name))
    
    CLI(net)

    net.stop()
    return
    
if __name__ == '__main__':

    main()