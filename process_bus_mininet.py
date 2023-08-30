"""Custom topology for a process bus

Below we should visualize the topology, with something like the following:
             host3
               |
               |
               |
   host1 --- switch --- host2

"""
import os
import sys
import threading
import time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

class process_bus( Topo ):
    def build( self ):

        # Add hosts and switches
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
            "487B_2": [],
            "487E_1": [],
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
            self.addLink( IED, switch1, cls=TCLink, bw=100)

        # Assigning IDS as well
        self.IDSs["IDS_1"].append(f"192.168.1.120/24")
        self.IDSs["IDS_1"].append(f"00:00:00:00:11:11")

        IDS = self.addHost( "IDS_1", ip=self.IDSs["IDS_1"][0], mac=self.IDSs["IDS_1"][1] )
        self.addLink( IDS, switch1, cls=TCLink, bw=100, port1=20, port2=20 )


# topos = { "process_bus": ( lambda: process_bus() ) }


def run_commands (host):
    host.cmd("tcpdump -i {0}-eth0 -w ./exp_1/exp_1_{0}.pcap &".format(host.name))
    time.sleep(0.1)
    host.cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic/goose_CHE_203_generic {0}-eth0 {0}' &".format(host.name))

def main(scenario=0, run=1, security=False):
    topo = process_bus()
    net = Mininet(topo, build=False, waitConnected=True )
    control = RemoteController('c0', ip='127.0.0.1', port=6633) 
    net.addController(control)
    net.build()
    net.start()

    multicast_mapping = {
        "RTAC" : "01:0c:cd:01:00:01"
    }

    prefix = ""
    if security == "True":
        prefix="security_"
    elif security == "False":
        prefix="learning_"


    scenario_1_hosts = ["787_2", "451_2", "RTAC", "651R_2", "IDS_1"]
    scenario_2_hosts = ["RTAC", "651R_2", "787_2", "451_2", "487B_2", "351_2"]
    
    hosts = net.hosts
    if scenario == 1:
        new_dir = "./scenario_1_exp/{0}scenario_1_exp_{1}".format(prefix, run)

        if not os.path.exists(new_dir):
            os.mkdir(new_dir)

        for host in hosts:
            # print(host.cmd("ip a"))
            # TODO: These are executed serially, need to be executed in parallel
            # (threads) so we will not loose packet on either sides.
            if host.name in scenario_1_hosts:
                host.cmd("tcpdump -i {0}-eth0 -w {1}/exp_{2}_{0}.pcap &".format(host.name, new_dir, run))
                time.sleep(0.2)
                # host.cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic/goose_CHE_203_generic {0}-eth0 {0}' &".format(host.name))

                # p1 = threading.Thread(target=run_commands, args=(host, ))
                # p1.start()
                # p1.join()
        
        # rtac = hosts[10]
        # rtac.cmd("tcpdump -i RTAC-eth0 -w ./exp_1/exp_1_RTAC.pcap &")

        # time.sleep(5)
        # # print("651R!!!!! {0}".format(hosts[7]))
        # dev_651R = hosts[7]
        # dev_651R.cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic/goose_CHE_203_generic 651R_2-eth0 651R_2' &")

        # for host in hosts:
        #     if host.name in scenario_1_hosts:
        #         host.cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic/goose_CHE_203_generic {0}-eth0 {0}' &".format(host.name))

        hosts[8].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic/goose_CHE_203_generic 787_2-eth0 787_2' &")
        hosts[3].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic/goose_CHE_203_generic 451_2-eth0 451_2' &")
        hosts[10].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic/goose_CHE_203_generic RTAC-eth0 RTAC' &")
        hosts[7].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic/goose_CHE_203_generic 651R_2-eth0 651R_2' &")
    
    elif scenario == 2:

        new_dir = "./scenario_2_exp_{0}".format(run)

        if not os.path.exists(new_dir):
            os.mkdir(new_dir)

        # We need to have this specific sequence to make sure the messages arrive in a proper order
        # Therefore we hardcode the commands.
        hosts[8].cmd("tcpdump -i 787_2-eth0 -w ./{0}/exp_{1}_787_2.pcap &".format(new_dir, run))
        time.sleep(0.1)
        hosts[8].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic_Scenario2/goose_CHE_203_787_2_Scenario2 787_2-eth0' &")
    
        hosts[3].cmd("tcpdump -i 451_2-eth0 -w ./{0}/exp_{1}_451_2.pcap &".format(new_dir, run))
        time.sleep(0.1)
        hosts[3].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic_Scenario2/goose_CHE_203_451_2_Scenario2 451_2-eth0' &")
    
        hosts[10].cmd("tcpdump -i RTAC-eth0 -w ./{0}/exp_{1}_RTAC.pcap &".format(new_dir, run))
        time.sleep(0.1)
        hosts[10].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic_Scenario2/goose_CHE_203_RTAC_Scenario2 RTAC-eth0' &")
    
        hosts[4].cmd("tcpdump -i 487B_2-eth0 -w ./{0}/exp_{1}_487B_2.pcap &".format(new_dir, run))
        time.sleep(0.1)
        hosts[4].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic_Scenario2/goose_CHE_203_487B_2_Scenario2 487B_2-eth0' &")
        
        hosts[1].cmd("tcpdump -i 351_2-eth0 -w ./{0}/exp_{1}_351_2.pcap &".format(new_dir, run))
        time.sleep(0.1)
        hosts[1].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic_Scenario2/goose_CHE_203_351_2_Scenario2 351_2-eth0' &")

        hosts[7].cmd("tcpdump -i 651R_2-eth0 -w ./{0}/exp_{1}_651R_2.pcap &".format(new_dir, run))
        time.sleep(0.1)
        hosts[7].cmd("bash -c '/home/mininet/substation_arch_test/goose_CHE_203_generic_Scenario2/goose_CHE_203_651R_2_Scenario2 651R_2-eth0' &")
        
        # print(hosts)
        # print(hosts[7].cmd("ip a"))

    # CLI(net)

    time.sleep(60)

    net.stop()
    return
    
if __name__ == '__main__':
    try:
        scenario = int(sys.argv[1])
        run = int(sys.argv[2])
        security = sys.argv[3]
    except ValueError as er:
        print("Provided arg is not a number.")
        exit(1)
    
    main(scenario=scenario, run=run, security=security)