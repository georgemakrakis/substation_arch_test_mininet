from mininet.net import Mininet
from mininet.link import TCIntf, Intf
from mininet.cli import CLI

net = Mininet( )
h1, h2 = net.addHost( 'h1' ), net.addHost( 'h2' )
l1 = net.addLink( h1, h2, intf=Intf, params1={ 'bw': 10 }, params2={ 'bw': 20 } )
print(l1.intf1, l1.intf2.MAC)
l1.intf1.setMAC ("00:00:00:00:00:02")
l1.intf2.setMAC ("00:00:00:00:00:03")
print(l1.intf1.MAC)
net.start()
CLI( net )
net.stop()