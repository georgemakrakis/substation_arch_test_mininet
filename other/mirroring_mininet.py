from mininet.topo import Topo

class simple_topo( Topo ):
     def build( self ):
        switch1 = self.addSwitch( "s1", protocols=["OpenFlow13"] )

        host1 = self.addHost( 'h1', ip="10.0.0.2", mac="00:00:00:00:00:02" )
        host2 = self.addHost( 'h2', ip="10.0.0.3", mac="00:00:00:00:00:03" )
        ids = self.addHost( 'IDS', ip="10.0.0.4", mac="00:00:00:00:00:04" )

        # Add links
        self.addLink( host1, switch1, port1=1, port2=1 )
        self.addLink( host2, switch1, port1=2, port2=2 )
        self.addLink( ids, switch1, port1=3, port2=3 )



topos = { "simple_topo": ( lambda: simple_topo() ) }