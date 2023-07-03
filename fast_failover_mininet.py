from mininet.topo import Topo

class failover_process_bus( Topo ):
    def build( self ):
        
        self.IEDs = {
            "487E": [],
            "RTAC":[]
        }

        IEDs_keys = list(self.IEDs.keys())
        
        switch1 = self.addSwitch( "s1", protocols=["OpenFlow13"] )
        switch2 = self.addSwitch( "s2", protocols=["OpenFlow13"] )

        # Adding the failover path link between the s1 and s2
        self.addLink(switch1, switch2, port1=20, port2=20 )


        # for i in range(len(self.IEDs)):
        #     # +5 casue we did already setup 5 TMUs in this subnet
        #     j = i + 7
            
        #     if j > 9:
        #         j_str = f"{j}"
        #     else:
        #         j_str = f"0{j}"

        #     self.IEDs[IEDs_keys[i]].append(f"192.168.1.{j}/24")
        #     self.IEDs[IEDs_keys[i]].append(f"00:00:00:00:00:{j_str}")

        # IED_1 = self.addHost("487E", ip="192.168.1.2/24", mac="00:00:00:00:00:02")
        # self.addLink( IED_1, switch1 )

        IED_1 = self.addHost("487E", ip=None, mac=None)
        # TODO: The MAC is not beeing assigned, need to fix this.
        self.addLink( IED_1, switch1, intfName1='487E-eth0', intfName2='s1-eth2', params1={'ip':'192.168.1.2/24'})
        self.addLink( IED_1, switch2, intfName1='487E-eth1', intfName2='s2-eth2', params1={'ip':'192.168.1.3/24'})

        IED_1 = self.addHost("RTAC", ip=None, mac=None)
        # TODO: The MAC is not beeing assigned, need to fix this.
        self.addLink( IED_1, switch1, intfName1='RTAC-eth0', intfName2='s1-eth3', params1={'ip':'192.168.1.4/24'})
        self.addLink( IED_1, switch2, intfName1='RTAC-eth1', intfName2='s2-eth3', params1={'ip':'192.168.1.5/24'})

        # IED_1= self.addHost("487E", ip="192.168.1.3/24", mac="00:00:00:00:00:03" )
        # self.addLink( IED_1, switch2 )

topos = { "failover_process_bus": ( lambda: failover_process_bus() ) }