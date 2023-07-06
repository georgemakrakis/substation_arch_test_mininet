from mininet.topo import Topo
from mininet.link import Link, Intf
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController, OVSSwitch

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

        IED_1 = self.addHost("487E", ip=None, mac=None)
        self.addLink( IED_1, switch1, intfName1='487E-eth0', intfName2='s1-eth2', params1={'ip':'192.168.1.2/24'})
        # NOTE: Do not assign a second interface for now.
        # self.addLink( IED_1, switch2, intfName1='487E-eth1', intfName2='s2-eth2', params1={'ip':'192.168.1.3/24'})
        
        
        IED_2 = self.addHost("RTAC", ip=None, mac=None)
        self.addLink( IED_2, switch1, intfName1='RTAC-eth0', intfName2='s1-eth3', params1={'ip':'192.168.1.4/24'})
        # NOTE: Have both interfaces of RTAC to the same switch for now
        self.addLink( IED_2, switch1, intfName1='RTAC-eth1', intfName2='s1-eth4', params1={'ip':'192.168.1.5/24'})
        # self.addLink( IED_2, switch2, intfName1='RTAC-eth1', intfName2='s2-eth3', params1={'ip':'192.168.1.5/24'})

#topos = { "failover_process_bus": ( lambda: failover_process_bus() ) }

net = Mininet( topo=failover_process_bus(), 
              controller=lambda name: RemoteController( name, ip='127.0.0.1' ), 
              switch=OVSSwitch,
              )
net.start()
# for h in '487E',:
#     net[ h].intfs[ 0 ].setMAC ("00:00:00:00:00:02")
#     net[ h ].intfs[ 1 ].setMAC ("00:00:00:00:00:03")

net[ '487E' ].intfs[ 0 ].setMAC ("00:00:00:00:00:02")
# NOTE: Do not assign a second interface for now.
# net[ '487E' ].intfs[ 1 ].setMAC ("00:00:00:00:00:03")

net[ 'RTAC' ].intfs[ 0 ].setMAC ("00:00:00:00:00:04")
net[ 'RTAC' ].intfs[ 1 ].setMAC ("00:00:00:00:00:05")

CLI( net )
net.stop()
