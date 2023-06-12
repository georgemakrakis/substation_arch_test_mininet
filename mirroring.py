from ryu.base import app_manager # This is the main entry point for the controller application.

from ryu.controller import ofp_event # To capture openflow event, when the openflow packet received
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls

from ryu.ofproto import ofproto_v1_3  # Specify the Openflow version to be used.


from ryu.lib.packet import packet
from ryu.lib.packet import ethernet


class L2_switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2_switch, self).__init__(*args, **kwargs)
        self.mac_to_port = {} # The mac address table is empty initially.


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install the table-miss flow entry
        match = parser.OFPMatch()

        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)


        # Install the flows for the mirroring of Ports 1 and 2 to Port 3 (where IDS lives).
        match_1 = parser.OFPMatch(in_port=1)
        actions_1 = [parser.OFPActionOutput(2), parser.OFPActionOutput(3)]

        self.add_flow(datapath, 100, match_1, actions_1)

        match_2 = parser.OFPMatch(in_port=2)
        actions_2 = [parser.OFPActionOutput(1), parser.OFPActionOutput(3)]

        self.add_flow(datapath, 100, match_2, actions_2)

        # Drop any traffic coming from Port 3
        match_3 = parser.OFPMatch(in_port=3)
        actions_3 = []

        self.add_flow(datapath, 0, match_3, actions_3)


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

        in_port = msg.match['in_port']

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # Learn a mac address so next time the packet will not be flooded
        self.mac_to_port[dpid][src] = in_port

        # if the destination mac address is already learned, send packe to specific port, otherwise flood it.
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        # The actions list
        actions = [parser.OFPActionOutput(out_port)]

        # Install a flow to the swtich to avoid packet_in to controller next time.
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        # Construct packet_out to switch message and send it
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions,
                                  data=msg.data)
        datapath.send_msg(out)
