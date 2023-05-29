from ryu.base import app_manager # This is the main entry point for the controller application.

from ryu.controller import ofp_event # To capture openflow event, when the openflow packet received
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls

from ryu.ofproto import ofproto_v1_3  # Specify the Openflow version to be used.


from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import in_proto

class process_bus(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(process_bus, self).__init__(*args, **kwargs)
        self.mac_to_port = {} # The mac address table is empty initially.

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        # ICMP drop flow example
        # match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ip_proto=in_proto.IPPROTO_ICMP)
        # mod = parser.OFPFlowMod(datapath=datapath, table_id=0, priority=10000, match=match)
        # datapath.send_msg(mod)

        # TODO: Shall we create an automated way using a few loops to apply all the default rules that we want?
        # Do it for ICMP first as an example until we figure out the usage of protocols.

        # <Host 351_1: 351_1-eth0:192.168.1.10 pid=64967> 
        # <Host 351_2: 351_2-eth0:192.168.1.9 pid=64969> 
        # <Host 451_1: 451_1-eth0:192.168.1.7 pid=64978> 
        # <Host 451_2: 451_2-eth0:192.168.1.8 pid=64996> 
        # <Host 487B: 487B-eth0:192.168.1.11 pid=64998> 
        # <Host 487E: 487E-eth0:192.168.1.12 pid=65000> 
        # <Host 651R_1: 651R_1-eth0:192.168.1.14 pid=65002> 
        # <Host 651R_2: 651R_2-eth0:192.168.1.15 pid=65021> 
        # <Host 787_2: 787_2-eth0:192.168.1.13 pid=65023> 
        # <Host RTAC: RTAC-eth0:192.168.1.16 pid=65025> 

        # <Host tmu1: tmu1-eth0:192.168.1.2 pid=65038> 
        # <Host tmu2: tmu2-eth0:192.168.1.3 pid=65040> 
        # <Host tmu3: tmu3-eth0:192.168.1.4 pid=65042> 
        # <Host tmu4: tmu4-eth0:192.168.1.5 pid=65044> 
        # <Host tmu5: tmu5-eth0:192.168.1.6 pid=65046>

        # TODO: Can we parse those from a CSV or JSON file?
        block_comms = [
            # For 351_1
            ("192.168.1.10", "192.168.1.7", "00:00:00:00:00:10", "00:00:00:00:00:07"),
            ("192.168.1.10", "192.168.1.5", "00:00:00:00:00:10", "00:00:00:00:00:05"),
            ("192.168.1.10", "192.168.1.9", "00:00:00:00:00:10", "00:00:00:00:00:09"),
            ("192.168.1.10", "192.168.1.11", "00:00:00:00:00:10", "00:00:00:00:00:11"),
            ("192.168.1.10", "192.168.1.12", "00:00:00:00:00:10", "00:00:00:00:00:12"),
            ("192.168.1.10", "192.168.1.13", "00:00:00:00:00:10", "00:00:00:00:00:13"),
            ("192.168.1.10", "192.168.1.2", "00:00:00:00:00:10", "00:00:00:00:00:02"),
            ("192.168.1.10", "192.168.1.4", "00:00:00:00:00:10", "00:00:00:00:00:04"),
            ("192.168.1.10", "192.168.1.8", "00:00:00:00:00:10", "00:00:00:00:00:08"),
            ("192.168.1.10", "192.168.1.6", "00:00:00:00:00:10", "00:00:00:00:00:06"),
            ("192.168.1.10", "192.168.1.14", "00:00:00:00:00:10", "00:00:00:00:00:14"),
            ("192.168.1.10", "192.168.1.15", "00:00:00:00:00:10", "00:00:00:00:00:15"),

            # For 351_2
            ("192.168.1.9", "192.168.1.8", "00:00:00:00:00:09", "00:00:00:00:00:08"),
            ("192.168.1.9", "192.168.1.6", "00:00:00:00:00:09", "00:00:00:00:00:06"),
            ("192.168.1.9", "192.168.1.7", "00:00:00:00:00:09", "00:00:00:00:00:07"),
            ("192.168.1.9", "192.168.1.10", "00:00:00:00:00:09", "00:00:00:00:00:10"),
            ("192.168.1.9", "192.168.1.11", "00:00:00:00:00:09", "00:00:00:00:00:11"),
            ("192.168.1.9", "192.168.1.12", "00:00:00:00:00:09", "00:00:00:00:00:12"),
            ("192.168.1.9", "192.168.1.13", "00:00:00:00:00:09", "00:00:00:00:00:13"),
            ("192.168.1.9", "192.168.1.2", "00:00:00:00:00:09", "00:00:00:00:00:02"),
            ("192.168.1.9", "192.168.1.4", "00:00:00:00:00:09", "00:00:00:00:00:04"),
            ("192.168.1.9", "192.168.1.3", "00:00:00:00:00:09", "00:00:00:00:00:03"),
            ("192.168.1.9", "192.168.1.6", "00:00:00:00:00:09", "00:00:00:00:00:06"),
            ("192.168.1.9", "192.168.1.14", "00:00:00:00:00:09", "00:00:00:00:00:14"),
            ("192.168.1.9", "192.168.1.15", "00:00:00:00:00:09", "00:00:00:00:00:15"),

            # For 451_1
            ("192.168.1.7", "192.168.1.8", "00:00:00:00:00:07", "00:00:00:00:00:08"),
            ("192.168.1.7", "192.168.1.6", "00:00:00:00:00:07", "00:00:00:00:00:06"),
            ("192.168.1.7", "192.168.1.9", "00:00:00:00:00:07", "00:00:00:00:00:07"),
            ("192.168.1.7", "192.168.1.10", "00:00:00:00:00:07", "00:00:00:00:00:10"),
            ("192.168.1.7", "192.168.1.11", "00:00:00:00:00:07", "00:00:00:00:00:11"),
            ("192.168.1.7", "192.168.1.12", "00:00:00:00:00:07", "00:00:00:00:00:12"),
            ("192.168.1.7", "192.168.1.13", "00:00:00:00:00:07", "00:00:00:00:00:13"),
            ("192.168.1.7", "192.168.1.2", "00:00:00:00:00:07", "00:00:00:00:00:02"),
            ("192.168.1.7", "192.168.1.4", "00:00:00:00:00:07", "00:00:00:00:00:04"),
            ("192.168.1.7", "192.168.1.3", "00:00:00:00:00:07", "00:00:00:00:00:03"),
            ("192.168.1.7", "192.168.1.6", "00:00:00:00:00:07", "00:00:00:00:00:06"),
            ("192.168.1.7", "192.168.1.14", "00:00:00:00:00:07", "00:00:00:00:00:14"),
            ("192.168.1.7", "192.168.1.15", "00:00:00:00:00:07", "00:00:00:00:00:15"),
            ("192.168.1.7", "192.168.1.5", "00:00:00:00:00:07", "00:00:00:00:00:05"),
            
        ]

        # for i in range(len(block_comms_IP)):
        #     print(f"{block_comms_IP[i][0]} with {block_comms_IP[i][1]}")
        #     print(f"and {block_comms_IP[i][1]} with {block_comms_IP[i][0]}")

        for i in range(len(block_comms)):
            match = parser.OFPMatch(
                eth_type = 0x0800,
                ipv4_src=(block_comms[i][0]),
                ipv4_dst=(block_comms[i][1]),
                eth_src=(block_comms[i][2]),
                eth_dst=(block_comms[i][3])
            )
            # Empty actions should apply to drop the packet
            actions = []
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS,
                                                actions)]
            
            mod = parser.OFPFlowMod(datapath=datapath, table_id=0, priority=2, match=match, instructions=inst)
            datapath.send_msg(mod)

            # NOTE: This is not needed since each device will decide where it talks based on the above
            # Also we might want to prevent comms to one direction only (e.g. 451_1 --> 351_1 but NOT 451_1 <-- 351_1)
            # Block the other side as well
            # match = parser.OFPMatch(
            #     eth_type = 0x0800,
            #     ipv4_src=(block_comms[i][1]),
            #     ipv4_dst=(block_comms[i][0]),
            #     eth_src=(block_comms[i][3]),
            #     eth_dst=(block_comms[i][2])
            # )
            # # Empty actions should apply to drop the packet
            # actions = []
            # inst = [parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS,
            #                                     actions)]
            
            # mod = parser.OFPFlowMod(datapath=datapath, table_id=0, priority=2, match=match, instructions=inst)
            # datapath.send_msg(mod)

        

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s SRC: %s DST: %s IN_PORT: %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)   