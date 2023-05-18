"""Custom topology for a process bus

Below we should visualize the topology, with somethink like the following:
             host3
               |
               |
               |
   host1 --- switch --- host2

"""

from mininet.topo import Topo

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
            "tidl1": [],
            "tidl2": [],
            "tidl3": [],
            "tidl4": [],
            "tidl5": []
        }

        self.IEDs = {
            "451_11_12": [],
            "387_11_12": [],
            "451_5_7": [],
            "351_9": [],
            "351_10": [],
            "487B_4_6_8": [],
            "487E_1_3": [],
            "787_2_4": [],
            "651R_1": [],
            "651R_2":[]
        }


        TMUs_keys = list(self.TMUs.keys())
        IEDs_keys = list(self.IEDs.keys())

        switch1 = self.addSwitch( "s1", protocols=["OpenFlow13"] )
        
        # Assign IPs and MACs, add hosts and links
        for i in range(5):
             # +2 to start from .2 address
            j = i + 2
            self.TMUs[TMUs_keys[i]].append(f"192.168.1.{j}/24")
            self.TMUs[TMUs_keys[i]].append(f"00:00:00:00:00:0{j}")

            TMU = self.addHost( TMUs_keys[i], ip=self.TMUs[TMUs_keys[i]][0], mac=self.TMUs[TMUs_keys[i]][1] )
            self.addLink( TMU, switch1 )
        
        for i in range(10):
            # +5 casue we did already setup 5 TMUs in this subnet
            j = i + 5
            self.IEDs[IEDs_keys[i]].append(f"192.168.1.{j}/24")
            self.IEDs[IEDs_keys[i]].append(f"00:00:00:00:00:0{j}")

            IED = self.addHost( IEDs_keys[i], ip=self.IEDs[IEDs_keys[i]][0], mac=self.IEDs[IEDs_keys[i]][1] )
            self.addLink( IED, switch1 )


topos = { "process_bus": ( lambda: process_bus() ) }
