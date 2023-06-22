import json, re, time, os
from io import BytesIO
import zipfile

from ryu.base import app_manager # This is the main entry point for the controller application.

from ryu.controller import ofp_event # To capture openflow event, when the openflow packet received
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls

from ryu.ofproto import ofproto_v1_3  # Specify the Openflow version to be used.

from ryu.lib import hub

from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import in_proto

from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from webob import Response

processBus_app_instance_name = 'processBus_app'
urlAll = '/processBus/getStats/{inPort}'
urlMeter = '/processBus/meter'
urlMeterStatsAll = '/processBus/getMeterStats'
urlModifyRule = '/processBus/modifyRule'

urlGetDefaultFlows = '/processBus/defaultFlows'
urlGetPacketInFlows = '/processBus/packetInFlows'
# TODO: Maybe the below not needed, can we use the urlMeter with GET?
urlGetMeterFlows = '/processBus/meterFlows'
urlGetDropFlows = '/processBus/dropFlows'

OFP_REPLY_TIMER = 1.0  # sec

class process_bus(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    block_comms = {}

    def __init__(self, *args, **kwargs):
        super(process_bus, self).__init__(*args, **kwargs)
        self.mac_to_port = {} # The mac address table is empty initially.

        wsgi = kwargs['wsgi']
        self.datapath = None
        self.flows_stats = []
        wsgi.register(ProcessBussController,
                      {processBus_app_instance_name: self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        self.datapath = ev.msg.datapath

        self.flows_stats = []
        self.meter_stats = []

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER), parser.OFPActionOutput(20)]
        
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        
        waiters = {}
        command = ofproto.OFPFC_ADD
        self.add_flow(datapath, 0, command, match, inst, waiters, "controller_handling", 0)

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

        # TODO: Can we parse each one of those from a CSV or JSON file?
        self.block_comms = [
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
            ("192.168.1.7", "192.168.1.9", "00:00:00:00:00:07", "00:00:00:00:00:09"),
            ("192.168.1.7", "192.168.1.10", "00:00:00:00:00:07", "00:00:00:00:00:10"),
            ("192.168.1.7", "192.168.1.11", "00:00:00:00:00:07", "00:00:00:00:00:11"),
            ("192.168.1.7", "192.168.1.12", "00:00:00:00:00:07", "00:00:00:00:00:12"),
            ("192.168.1.7", "192.168.1.13", "00:00:00:00:00:07", "00:00:00:00:00:13"),
            ("192.168.1.7", "192.168.1.2", "00:00:00:00:00:07", "00:00:00:00:00:02"),
            ("192.168.1.7", "192.168.1.4", "00:00:00:00:00:07", "00:00:00:00:00:04"),
            ("192.168.1.7", "192.168.1.3", "00:00:00:00:00:07", "00:00:00:00:00:03"),
            ("192.168.1.7", "192.168.1.14", "00:00:00:00:00:07", "00:00:00:00:00:14"),
            ("192.168.1.7", "192.168.1.15", "00:00:00:00:00:07", "00:00:00:00:00:15"),
            ("192.168.1.7", "192.168.1.5", "00:00:00:00:00:07", "00:00:00:00:00:05"),

            # For 451_2
            ("192.168.1.8", "192.168.1.7", "00:00:00:00:00:08", "00:00:00:00:00:07"),
            ("192.168.1.8", "192.168.1.9", "00:00:00:00:00:08", "00:00:00:00:00:09"),
            ("192.168.1.8", "192.168.1.10", "00:00:00:00:00:08", "00:00:00:00:00:10"),
            ("192.168.1.8", "192.168.1.11", "00:00:00:00:00:08", "00:00:00:00:00:11"),
            ("192.168.1.8", "192.168.1.12", "00:00:00:00:00:08", "00:00:00:00:00:12"),
            ("192.168.1.8", "192.168.1.13", "00:00:00:00:00:08", "00:00:00:00:00:13"),
            ("192.168.1.8", "192.168.1.2", "00:00:00:00:00:08", "00:00:00:00:00:02"),
            ("192.168.1.8", "192.168.1.6", "00:00:00:00:00:08", "00:00:00:00:00:06"),
            ("192.168.1.8", "192.168.1.14", "00:00:00:00:00:08", "00:00:00:00:00:14"),
            ("192.168.1.8", "192.168.1.15", "00:00:00:00:00:08", "00:00:00:00:00:15"),

            # For 651R_1
            ("192.168.1.14", "192.168.1.8", "00:00:00:00:00:14", "00:00:00:00:00:08"),
            ("192.168.1.14", "192.168.1.6", "00:00:00:00:00:14", "00:00:00:00:00:06"),
            ("192.168.1.14", "192.168.1.9", "00:00:00:00:00:14", "00:00:00:00:00:09"),
            ("192.168.1.14", "192.168.1.10", "00:00:00:00:00:14", "00:00:00:00:00:10"),
            ("192.168.1.14", "192.168.1.11", "00:00:00:00:00:14", "00:00:00:00:00:11"),
            ("192.168.1.14", "192.168.1.12", "00:00:00:00:00:14", "00:00:00:00:00:12"),
            ("192.168.1.14", "192.168.1.13", "00:00:00:00:00:14", "00:00:00:00:00:13"),
            ("192.168.1.14", "192.168.1.2", "00:00:00:00:00:14", "00:00:00:00:00:02"),
            ("192.168.1.14", "192.168.1.4", "00:00:00:00:00:14", "00:00:00:00:00:04"),
            ("192.168.1.14", "192.168.1.3", "00:00:00:00:00:14", "00:00:00:00:00:03"),
            ("192.168.1.14", "192.168.1.6", "00:00:00:00:00:14", "00:00:00:00:00:06"),
            ("192.168.1.14", "192.168.1.7", "00:00:00:00:00:14", "00:00:00:00:00:07"),
            ("192.168.1.14", "192.168.1.15", "00:00:00:00:00:14", "00:00:00:00:00:15"),
            ("192.168.1.14", "192.168.1.5", "00:00:00:00:00:14", "00:00:00:00:00:05"),

            # For 651R_2
            ("192.168.1.15", "192.168.1.8", "00:00:00:00:00:15", "00:00:00:00:00:08"),
            ("192.168.1.15", "192.168.1.6", "00:00:00:00:00:15", "00:00:00:00:00:06"),
            ("192.168.1.15", "192.168.1.9", "00:00:00:00:00:15", "00:00:00:00:00:09"),
            ("192.168.1.15", "192.168.1.10", "00:00:00:00:00:15", "00:00:00:00:00:10"),
            ("192.168.1.15", "192.168.1.11", "00:00:00:00:00:15", "00:00:00:00:00:11"),
            ("192.168.1.15", "192.168.1.12", "00:00:00:00:00:15", "00:00:00:00:00:12"),
            ("192.168.1.15", "192.168.1.13", "00:00:00:00:00:15", "00:00:00:00:00:13"),
            ("192.168.1.15", "192.168.1.2", "00:00:00:00:00:15", "00:00:00:00:00:02"),
            ("192.168.1.15", "192.168.1.4", "00:00:00:00:00:15", "00:00:00:00:00:04"),
            ("192.168.1.15", "192.168.1.3", "00:00:00:00:00:15", "00:00:00:00:00:03"),
            ("192.168.1.15", "192.168.1.6", "00:00:00:00:00:15", "00:00:00:00:00:06"),
            ("192.168.1.15", "192.168.1.7", "00:00:00:00:00:15", "00:00:00:00:00:07"),
            ("192.168.1.15", "192.168.1.14", "00:00:00:00:00:15", "00:00:00:00:00:14"),
            ("192.168.1.15", "192.168.1.5", "00:00:00:00:00:15", "00:00:00:00:00:05"),

            # For 487B
            ("192.168.1.11", "192.168.1.7", "00:00:00:00:00:11", "00:00:00:00:00:07"),
            ("192.168.1.11", "192.168.1.9", "00:00:00:00:00:11", "00:00:00:00:00:09"),
            ("192.168.1.11", "192.168.1.10", "00:00:00:00:00:11", "00:00:00:00:00:10"),
            ("192.168.1.11", "192.168.1.8", "00:00:00:00:00:11", "00:00:00:00:00:08"),
            ("192.168.1.11", "192.168.1.12", "00:00:00:00:00:11", "00:00:00:00:00:12"),
            ("192.168.1.11", "192.168.1.13", "00:00:00:00:00:11", "00:00:00:00:00:13"),
            ("192.168.1.11", "192.168.1.2", "00:00:00:00:00:11", "00:00:00:00:00:02"),
            ("192.168.1.11", "192.168.1.6", "00:00:00:00:00:11", "00:00:00:00:00:06"),
            ("192.168.1.11", "192.168.1.14", "00:00:00:00:00:11", "00:00:00:00:00:14"),
            ("192.168.1.11", "192.168.1.15", "00:00:00:00:00:11", "00:00:00:00:00:15"),

            # For 487E
            ("192.168.1.12", "192.168.1.7", "00:00:00:00:00:12", "00:00:00:00:00:07"),
            ("192.168.1.12", "192.168.1.9", "00:00:00:00:00:12", "00:00:00:00:00:09"),
            ("192.168.1.12", "192.168.1.10", "00:00:00:00:00:12", "00:00:00:00:00:10"),
            ("192.168.1.12", "192.168.1.11", "00:00:00:00:00:12", "00:00:00:00:00:11"),
            ("192.168.1.12", "192.168.1.8", "00:00:00:00:00:12", "00:00:00:00:00:08"),
            ("192.168.1.12", "192.168.1.13", "00:00:00:00:00:12", "00:00:00:00:00:13"),
            ("192.168.1.12", "192.168.1.4", "00:00:00:00:00:12", "00:00:00:00:00:04"),
            ("192.168.1.12", "192.168.1.5", "00:00:00:00:00:12", "00:00:00:00:00:05"),
            ("192.168.1.12", "192.168.1.6", "00:00:00:00:00:12", "00:00:00:00:00:06"),
            ("192.168.1.12", "192.168.1.14", "00:00:00:00:00:12", "00:00:00:00:00:14"),
            ("192.168.1.12", "192.168.1.15", "00:00:00:00:00:12", "00:00:00:00:00:15"),

            # For 787_2
            ("192.168.1.13", "192.168.1.7", "00:00:00:00:00:13", "00:00:00:00:00:07"),
            ("192.168.1.13", "192.168.1.9", "00:00:00:00:00:13", "00:00:00:00:00:09"),
            ("192.168.1.13", "192.168.1.10", "00:00:00:00:00:13", "00:00:00:00:00:10"),
            ("192.168.1.13", "192.168.1.11", "00:00:00:00:00:13", "00:00:00:00:00:11"),
            ("192.168.1.13", "192.168.1.8", "00:00:00:00:00:13", "00:00:00:00:00:08"),
            ("192.168.1.13", "192.168.1.12", "00:00:00:00:00:13", "00:00:00:00:00:12"),
            ("192.168.1.13", "192.168.1.2", "00:00:00:00:00:13", "00:00:00:00:00:2"),
            ("192.168.1.13", "192.168.1.3", "00:00:00:00:00:13", "00:00:00:00:00:03"),
            ("192.168.1.13", "192.168.1.4", "00:00:00:00:00:13", "00:00:00:00:00:04"),
            ("192.168.1.13", "192.168.1.14", "00:00:00:00:00:13", "00:00:00:00:00:14"),
            ("192.168.1.13", "192.168.1.15", "00:00:00:00:00:13", "00:00:00:00:00:15"),
        ]

        # NOTE: The below is not bidirectional !!!

        for i in range(len(self.block_comms)):
            match = parser.OFPMatch(
                eth_type = 0x0800,
                ipv4_src=(self.block_comms[i][0]),
                ipv4_dst=(self.block_comms[i][1]),
                eth_src=(self.block_comms[i][2]),
                eth_dst=(self.block_comms[i][3])
            )
            # Empty actions will apply to drop the packet
            actions = []
            # TODO: Shal we just forward it to the IDS (port 20) to create an alert anyways?
            # actions = [ofp_parser.OFPActionOutput(20)]

            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                                actions)]
            
            # TODO: Need to check the datapath IDs here so we will not apply the same rules to all switches.
            mod = parser.OFPFlowMod(datapath=datapath, table_id=0, priority=i, match=match, instructions=inst)
            datapath.send_msg(mod)

            # NOTE: Not sure about moving this one to the add_flow() yet.
            # waiters = {}
            # self.add_flow(datapath, 0, match, inst, waiters, "controller_handling")

            self.flow_log("default_flows", mod.to_jsondict())

            # NOTE: This is not needed since each device will decide where it talks based on the above
            # Also we might want to prevent comms to one direction only (e.g. 451_1 --> 351_1 but NOT 451_1 <-- 351_1)
            # Block the other side as well
            # match = parser.OFPMatch(
            #     eth_type = 0x0800,
            #     ipv4_src=(self.block_comms[i][1]),
            #     ipv4_dst=(self.block_comms[i][0]),
            #     eth_src=(self.block_comms[i][3]),
            #     eth_dst=(self.block_comms[i][2])
            # )
            # # Empty actions should apply to drop the packet
            # actions = []
            # inst = [parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS,
            #                                     actions)]
            
            # mod = parser.OFPFlowMod(datapath=datapath, table_id=0, priority=2, match=match, instructions=inst)
            # datapath.send_msg(mod)

        # Drop any traffic coming from Port 20 wich is the IDS
        match_3 = parser.OFPMatch(in_port=20)
        actions_3 = []
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                            actions_3)]

        self.add_flow(datapath, 3, command, match_3, inst, waiters, "IDS_drop", 0)

        

    def add_flow(self, datapath, priority, command, match, inst, waiters, log_action, table_id=0, timeout=OFP_REPLY_TIMER, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
        #                                      actions)]

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, command=command, buffer_id=buffer_id,
                                    priority=priority, match=match, table_id=table_id,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, command=command, priority=priority,
                                    match=match, table_id=table_id, instructions=inst)
        # datapath.send_msg(mod)

        # self.flow_log("add_flow", mod.to_jsondict())

        waiters_per_datapath = waiters.setdefault(datapath.id, {})
        event = hub.Event()
        msgs = []
        waiters_per_datapath[mod.xid] = (event, msgs)

        datapath.send_msg(mod)
        
        try:
            event.wait(timeout=timeout)
            self.flow_log(f"{log_action}", mod.to_jsondict())
        except hub.Timeout:
            del waiters_per_datapath[mod.xid]
            self.flow_log(f"{log_action}", mod.to_jsondict())
        except Exception as ex:
            print(f"set_meter exception: {ex}")
        


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

        self.logger.info("packet in switch %s SRC: %s DST: %s IN_PORT: %s", dpid, src, dst, in_port)
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            self.logger.info("with protocol ARP")
            
        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        # NOTE: Port 20 is the IDS
        actions = [parser.OFPActionOutput(out_port), parser.OFPActionOutput(20)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        command=ofproto.OFPFC_ADD
        waiters = {}

        block_exists = [tuple for tuple in self.block_comms if any(dst == i for i in tuple) and any(src == i for i in tuple)]

        if (not block_exists):

            # install a flow to avoid packet_in next time
            if out_port != ofproto.OFPP_FLOOD:
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 1, command, match, inst, waiters, "packet_in", 0, 0, msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath, 1, command, match, inst, waiters, "packet_in", 0, 0)
                
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)


    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        flows = []
        for stat in ev.msg.body:
            flows.append('table_id=%s '
                        'duration_sec=%d duration_nsec=%d '
                        'priority=%d '
                        'idle_timeout=%d hard_timeout=%d flags=0x%04x '
                        'cookie=%d packet_count=%d byte_count=%d '
                        'match=%s instructions=%s' %
                        (stat.table_id,
                        stat.duration_sec, stat.duration_nsec,
                        stat.priority,
                        stat.idle_timeout, stat.hard_timeout, stat.flags,
                        stat.cookie, stat.packet_count, stat.byte_count,
                        stat.match, stat.instructions))
        self.logger.debug('FlowStats: %s', flows)

        self.flows_stats = flows

    @set_ev_cls(ofp_event.EventOFPMeterStatsReply, MAIN_DISPATCHER)
    def meter_stats_reply_handler(self, ev):
        meters = []
        for stat in ev.msg.body:
            meters.append('meter_id=0x%08x len=%d flow_count=%d '
                        'packet_in_count=%d byte_in_count=%d '
                        'duration_sec=%d duration_nsec=%d '
                        'band_stats=%s' %
                        (stat.meter_id, stat.len, stat.flow_count,
                        stat.packet_in_count, stat.byte_in_count,
                        stat.duration_sec, stat.duration_nsec,
                        stat.band_stats))
        self.logger.debug('MeterStats: %s', meters)

        self.meter_stats = meters

    def flow_log(self, origin, flow_json):
        # Using 4 spaces as the "standard"
        json_object = json.dumps(flow_json, indent=4)
        
        path = origin
        if not os.path.exists(path):
            os.makedirs(path)

        with open(f"{path}/json_mod_{origin}_{time.strftime('%Y%m%d-%H%M%S')}.json", "w") as json_file:
            json_file.write(json_object)

    def set_metering(self, datapath, waiters, ether_dst, ether_src, priority, table_id):
        ofp_parser = datapath.ofproto_parser
        ofp = datapath.ofproto

        # Setting the meter here
        bands = []
        dropband = ofp_parser.OFPMeterBandDrop(rate=2, burst_size=1)
        bands.append(dropband)
        meter_request = ofp_parser.OFPMeterMod(datapath=datapath,
                                        command=ofp.OFPMC_ADD,
                                        flags=ofp.OFPMF_PKTPS,
                                        meter_id=1,
                                        bands=bands)
        datapath.send_msg(meter_request)

        #now meter_id=1 will be applied to the flow of in_port 1

        match = ofp_parser.OFPMatch(in_port=1, eth_dst=ether_dst, eth_src=ether_src)

        # TODO: So we will not have hardcoded ports next.
        # if dst in self.mac_to_port[dpid]:
        #     out_port = self.mac_to_port[dpid][dst]

        actions = [ofp_parser.OFPActionOutput(11), ofp_parser.OFPActionOutput(20)]

        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions),ofp_parser.OFPInstructionMeter(1)]
        
        command=ofp.OFPFC_MODIFY
        self.add_flow(datapath, priority, command, match, inst, waiters, "set_meter", table_id, OFP_REPLY_TIMER)

        # waiters_per_datapath = waiters.setdefault(datapath.id, {})
        # event = hub.Event()
        # msgs = []
        # waiters_per_datapath[ICMP_port1_mod.xid] = (event, msgs)

        # datapath.send_msg(ICMP_port1_mod)
        
        # try:
        #     event.wait(timeout=OFP_REPLY_TIMER)
        #     self.flow_log("set_meter", ICMP_port1_mod.to_jsondict())
        # except hub.Timeout:
        #     del waiters_per_datapath[ICMP_port1_mod.xid]
        #     self.flow_log("msg_timeout_set_meter", ICMP_port1_mod.to_jsondict())
        # except Exception as ex:
        #     print(f"set_meter exception: {ex}")
    

    def send_flow_stats_request(self, datapath, in_port, waiters):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        cookie = cookie_mask = 0
        
        if in_port:
            try:
                in_port_int = int(in_port)
                match = ofp_parser.OFPMatch()
                
                if in_port_int != 0:
                    match = ofp_parser.OFPMatch(in_port=in_port_int)
            except ValueError as er:
                print("The provided in_port is not a number")
        
        req = ofp_parser.OFPFlowStatsRequest(datapath, 0,
                                            ofp.OFPTT_ALL,
                                            ofp.OFPP_ANY, ofp.OFPG_ANY,
                                            cookie, cookie_mask,
                                            match)
        
        waiters_per_datapath = waiters.setdefault(datapath.id, {})
        event = hub.Event()
        msgs = []
        waiters_per_datapath[req.xid] = (event, msgs)

        datapath.send_msg(req)
        
        try:
            event.wait(timeout=OFP_REPLY_TIMER)
        except hub.Timeout:
            del waiters_per_datapath[req.xid]
            self.flow_log("msg_timeout_send_flow_stats_request", req.to_jsondict())
        except Exception as ex:
            print(f"send_flow_stats_request exception: {ex}")

    def send_meter_stats_request(self, datapath, waiters):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPMeterStatsRequest(datapath, 0, ofp.OFPM_ALL)

        waiters_per_datapath = waiters.setdefault(datapath.id, {})
        event = hub.Event()
        msgs = []
        waiters_per_datapath[req.xid] = (event, msgs)

        datapath.send_msg(req)
        
        try:
            
            event.wait(timeout=OFP_REPLY_TIMER)
        except hub.Timeout:
            del waiters_per_datapath[req.xid]
            self.flow_log("msg_timeout_send_meter_stats_request", req.to_jsondict())
        except Exception as ex:
            print(f"send_meter_stats_request exception: {ex}")


    def modify_drop_packets(self, datapath, waiters, ether_dst, ether_src, priority, table_id):
        ofp_parser = datapath.ofproto_parser
        ofp = datapath.ofproto
        
        # NOTE: All the below are for a very specific flow, need to generalize
        match = ofp_parser.OFPMatch(eth_dst=ether_dst, eth_src=ether_src)

        # TODO: Shal we just forward it to the IDS (port 20) to create an alert anyways?
        # actions = [ofp_parser.OFPActionOutput(20)]
        actions = []

        # inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,
        #                                      actions)]
        
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_CLEAR_ACTIONS,
                                             actions)]

        # NOTE: The above "TODO" questions are still valid and need to be addressed.
        command=ofp.OFPFC_MODIFY
        self.add_flow(datapath, priority, command, match, inst, waiters, "drop_packets", table_id)
 
        # waiters_per_datapath = waiters.setdefault(datapath.id, {})
        # event = hub.Event()
        # msgs = []
        # waiters_per_datapath[drop_mod.xid] = (event, msgs)

        # datapath.send_msg(drop_mod)
        
        # try:
            
        #     event.wait(timeout=OFP_REPLY_TIMER)
        #     self.flow_log("drop_packets", drop_mod.to_jsondict())
        # except hub.Timeout:
        #     del waiters_per_datapath[drop_mod.xid]
        #     self.flow_log("msg_timeout_drop_packets", drop_mod.to_jsondict())
        # except Exception as ex:
        #     print(f"modify_drop_packets exception: {ex}")

class ProcessBussController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(ProcessBussController, self).__init__(req, link, data, **config)
        self.process_bus_app = data[processBus_app_instance_name]

    def generate_zip(self, path):
        mem_zip = BytesIO()

        with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(path):
                for file in files:
                    # zf.writestr(file)
                    zf.write(f"./{path}/{file}")

        return mem_zip.getvalue()

    def validate_POST(self, json_req):

        tuple_ret = ()

        if "eth_dst" not in json_req or "eth_src" not in json_req or "priority" not in json_req or "table_id" not in json_req:
            # return Response(content_type='text/plain',status=400, body='Format should be: "eth_dst": "00:00:00:00:00:00", "eth_src": "00:00:00:00:00:00", "priority" : 0, "table_id" : 0\n')
            return ()
        
        for key, value in json_req.items():

            if (key == "eth_src"):
                # Regex from https://stackoverflow.com/a/7629690/7189378
                if not re.match("[0-9a-f]{2}([:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", value.lower()):
                    # return Response(content_type='text/plain',status=400, body='MAC Address should be in form: "00:00:00:00:00:00"\n')
                    return ()
                # eth_src = value
                tuple_ret = tuple_ret + (value,)
                
            if (key == "eth_dst"):
                if not re.match("[0-9a-f]{2}([:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", value.lower()):
                    # return Response(content_type='text/plain',status=400, body='MAC Address should be in form: "00:00:00:00:00:00"\n')
                    return ()                    
                # eth_dst = value
                tuple_ret = tuple_ret + (value,)

            if (key == "priority"):
                # priority = value
                tuple_ret = tuple_ret + (value,)

            if (key == "table_id"):
                # table_id = value
                tuple_ret = tuple_ret + (value,)

        # print(f"AAAAAA {tuple_ret}")
        return tuple_ret


    @route('processBus', urlAll, methods=['GET'])
    def get_flow_stats(self, req, **kwargs):
        datapath = self.process_bus_app.datapath
        in_port = kwargs['inPort']

        waiters = {}
        
        self.process_bus_app.send_flow_stats_request(datapath, in_port, waiters)

        process_bus_app = self.process_bus_app
        flows_stats = process_bus_app.flows_stats
        body = json.dumps(flows_stats)

        return Response(content_type='text/json', body=body)
        # return Response(content_type='text/plain', body="OK\n")

    # TODO: This is POST bue we do not realy pass any data, should be done.
    @route('processBus', urlMeter, methods=['POST'])
    def set_meter(self, req, **kwards):
        datapath = self.process_bus_app.datapath
        waiters = {}

        eth_dst = ""
        eth_src = ""
        priority = ""
        table_id = ""

        if (req.json):
            valid_tuple = self.validate_POST(req.json)
            if (len(valid_tuple) != 4):
                return Response(content_type='text/plain',status=400, body='Format should be: "eth_dst": "00:00:00:00:00:00", "eth_src": "00:00:00:00:00:00", "priority" : 0, "table_id" : 0\n')

            eth_dst, eth_src, priority, table_id = valid_tuple
            self.process_bus_app.set_metering(datapath, waiters, eth_dst, eth_src, priority, table_id)

            process_bus_app = self.process_bus_app
            # meter_stats = process_bus_app.meter_stats
            # body = json.dumps(meter_stats)

            return Response(content_type='text/plain', body='OK\n')

        else:
            # TODO: Shall we also include an informational message?
            return Response(content_type='text/plain',status=400)

        return Response(content_type='text/plain', body='OK\n')

    @route('processBus', urlMeterStatsAll, methods=['GET'])
    def get_meter_stats(self, req, **kwargs):
        datapath = self.process_bus_app.datapath
        waiters = {}
        
        self.process_bus_app.send_meter_stats_request(datapath, waiters)

        process_bus_app = self.process_bus_app
        meter_stats = process_bus_app.meter_stats
        body = json.dumps(meter_stats)

        return Response(content_type='text/json', body=body)
        # return Response(content_type='text/plain', body="OK\n")

    @route('processBus', urlModifyRule, methods=['POST'])
    def drop_packets(self, req, **kwargs):

        datapath = self.process_bus_app.datapath
        waiters = {}

        eth_dst = ""
        eth_src = ""
        priority = ""
        table_id = ""

        if (req.json):
            valid_tuple = self.validate_POST(req.json)
            if (len(valid_tuple) != 4):
                return Response(content_type='text/plain',status=400, body='Format should be: "eth_dst": "00:00:00:00:00:00", "eth_src": "00:00:00:00:00:00", "priority" : 0, "table_id" : 0\n')

            eth_dst, eth_src, priority, table_id = valid_tuple
            self.process_bus_app.modify_drop_packets(datapath, waiters, eth_dst, eth_src, priority, table_id)

            process_bus_app = self.process_bus_app
            # meter_stats = process_bus_app.meter_stats
            # body = json.dumps(meter_stats)

            return Response(content_type='text/plain', body='OK\n')

        else:
            # TODO: Shall we also include an informational message?
            return Response(content_type='text/plain',status=400)
        


    # Below are the endpoints for retrieving the flows log.

    @route('processBus', urlGetDefaultFlows, methods=['GET'])
    def get_default_flows(self, req, **kwargs):

        full_zip_in_memory = self.generate_zip("default_flows")
        
        response = Response(full_zip_in_memory, content_type='application/force-download')
        return response
    
    @route('processBus', urlGetPacketInFlows, methods=['GET'])
    def get_packetIn_flows(self, req, **kwargs):

        full_zip_in_memory = self.generate_zip("packet_in")
        
        response = Response(full_zip_in_memory, content_type='application/force-download')
        return response
    
    @route('processBus', urlGetMeterFlows, methods=['GET'])
    def get_meter_flows(self, req, **kwargs):

        full_zip_in_memory = self.generate_zip("set_meter")
        
        response = Response(full_zip_in_memory, content_type='application/force-download')
        return response
    
    @route('processBus', urlGetDropFlows, methods=['GET'])
    def get_packetIn_Flows(self, req, **kwargs):

        full_zip_in_memory = self.generate_zip("drop_packets")
        
        response = Response(full_zip_in_memory, content_type='application/force-download')
        return response