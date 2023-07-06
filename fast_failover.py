from ryu.base import app_manager # This is the main entry point for the controller application.

from ryu.controller import ofp_event # To capture openflow event, when the openflow packet received
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls

from ryu.ofproto import ofproto_v1_3  # Specify the Openflow version to be used.


from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import ether_types


class fast_failover_switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(fast_failover_switch, self).__init__(*args, **kwargs)
        self.datapaths = []
        self.mac_to_port = {} # The mac address table is empty initially.


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        print(f"New Datapath {datapath}")
        self.datapaths.append(datapath)

        # Install the table-miss flow entry
        match = parser.OFPMatch()

        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        # Add the group for fast failover
        actions1 = [parser.OFPActionOutput(3)]
        actions2 = [parser.OFPActionOutput(20)]
        # actions2 = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
        #                                   ofproto.OFPCML_NO_BUFFER)
        #                                   parser.OFPActionOutput(4)]

        weight = 0
        watch_port = 3
        watch_group = 0
        buckets = [parser.OFPBucket(watch_port=watch_port, watch_group=watch_group,
                                    actions=actions1),
                    # parser.OFPBucket(weight, 20, watch_group,
                    #                 actions2)
                    parser.OFPBucket(watch_port=20, watch_group=watch_group,
                                    actions=actions2)
                                    ]

        req = parser.OFPGroupMod(datapath=datapath, command=ofproto.OFPGC_ADD,
                                 type_=ofproto.OFPGT_FF, group_id=1, 
                                 buckets=buckets)
        datapath.send_msg(req)

        # Send the ARP packet to the controller for flooding
        # match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP)
        # actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
        #                                   ofproto.OFPCML_NO_BUFFER)]
        # self.add_flow(datapath, 11, match, actions)

        # Add the rest of the rules proaactively fow now.
        match = parser.OFPMatch(in_port=2)
        actions = [ parser.OFPActionGroup(group_id=1)]
        self.add_flow(datapath, 10, match, actions)

        if datapath.id == 2:
            match = parser.OFPMatch(in_port=20)
            actions = [ parser.OFPActionGroup(group_id=1)]
            self.add_flow(datapath, 9, match, actions)

        # match = parser.OFPMatch(in_port=3)
        # # actions = [ parser.OFPActionGroup(group_id=1)]
        # actions = [parser.OFPActionOutput(2)]
        # self.add_flow(datapath, 9, match, actions)

        # match = parser.OFPMatch(in_port=4)
        # # actions = [ parser.OFPActionGroup(group_id=1)]
        # actions = [parser.OFPActionOutput(2)]
        # self.add_flow(datapath, 8, match, actions)

        # match = parser.OFPMatch(in_port=4)
        # actions = [ parser.OFPActionGroup(group_id=1)]
        # self.add_flow(datapath, 8, match, actions)


    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Construct flow message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        dpid = datapath.id # Parse the Datapath ID to identify OpenFlow switches.
        self.mac_to_port.setdefault(dpid, {})

        # Analyze the received packets using the packet library.
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        dst = eth_pkt.dst
        src = eth_pkt.src

        # IP_pkt = pkt.get_protocol(ipv4.ipv4)
        # IP_dst = IP_pkt.dst
        # IP_src = IP_pkt.src

        in_port = msg.match['in_port']

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # Learn a mac address so next time the packet will not be flooded
        self.mac_to_port[dpid][src] = in_port

        # NOTE: Hardcoded statement for a specific MAC adddress
        # if dst == "00:00:00:00:00:04" and in_port == 20 and datapath.id == 2:
        # if dst == "00:00:00:00:00:04" and in_port == 2:
        #     print("ALTERNATIVE PATH!!!!!!!!!")
        #     #eth_pkt.dst = "00:00:00:00:00:05"
        #     #dst = "00:00:00:00:00:05"
        #     #out_port = 3
        #     # change datapath (NOTE: that works only for 2 switches/datapaths)
        #     #datapaths = [x for i,x in enumerate(self.datapaths) if x!=datapath]
        #     #datapath = datapaths[0]
        #     #print(f"DATAPATH ID{datapath.id}")

        #     actions_modify_headers = [parser.OFPActionSetField(eth_dst="00:00:00:00:00:05"),
        #                               parser.OFPActionSetField(ipv4_dst="192.168.1.5"),
        #                               parser.OFPActionOutput(4)
        #     ]
        #     match1 = parser.OFPMatch(eth_type=0x0800, in_port=2, eth_dst="00:00:00:00:00:04")
        #     self.add_flow(datapath, 11, match1, actions_modify_headers)
        #     out = parser.OFPPacketOut(datapath=datapath,
        #                               buffer_id=msg.buffer_id,
        #                               in_port=in_port, 
        #                               actions=actions_modify_headers, data=msg.data)
        #     datapath.send_msg(out)
        #     return
        # elif dst == "00:00:00:00:00:02" and in_port == 20 and datapath.id == 1:
        #     print("ALTERNATIVE PATH 2 !!!!!!!!!")

        #     actions = [parser.OFPActionOutput(2)]
        #     match1 = parser.OFPMatch(eth_type=0x0800, in_port=20, eth_dst="00:00:00:00:00:02")
        #     self.add_flow(datapath, 1, match1, actions)
        #     out = parser.OFPPacketOut(datapath=datapath,
        #                               buffer_id=msg.buffer_id,
        #                               in_port=in_port, 
        #                               actions=actions, data=msg.data)
        #     datapath.send_msg(out)
        #     return
        
        # if the destination mac address is already learned, send packet to specific port, otherwise flood it.
        # elif dst in self.mac_to_port[dpid]:

        # if eth_pkt.ethertype == ether_types.ETH_TYPE_ARP:

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        # The actions list
        # actions = [parser.OFPActionOutput(out_port)]
        actions = [parser.OFPActionOutput(out_port), parser.OFPActionGroup(group_id=1)]

        # Install a flow to the switch to avoid packet_in to controller next time.
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath, 1, match, actions)

        # Construct packet_out to switch message and send it
        out = parser.OFPPacketOut(datapath=datapath,
                                buffer_id=ofproto.OFP_NO_BUFFER,
                                in_port=in_port, actions=actions,
                                data=msg.data)
        datapath.send_msg(out)