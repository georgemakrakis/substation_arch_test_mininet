from ryu.base import app_manager # This is the main entry point for the controller application.

from ryu.controller import ofp_event # To capture openflow event, when the openflow packet received
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls

from ryu.ofproto import ofproto_v1_3  # Specify the Openflow version to be used.

from ryu.lib import hub
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

from ryu import cfg

OFP_REPLY_TIMER = 1.0  # sec

class learning_controller(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {}

    block_comms = {}

    def __init__(self, *args, **kwargs):
        super(learning_controller, self).__init__(*args, **kwargs)
        self.datapaths = []
        self.mac_to_port = {} # The mac address table is empty initially.

        CONF = cfg.CONF
        CONF.register_opts([
            cfg.IntOpt('scenario', default=1, help = ('Choosing scenario'))
        ])

        if (CONF.scenario):
            self.scenario = CONF.scenario

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        print(f"New Datapath {datapath}")
        self.datapaths.append(datapath)

        print("DATAPATH ID: ", datapath.id)

        self.datapath = datapath

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        
        waiters = {}
        command = ofproto.OFPFC_ADD

        # Table 0 is the ACL and Table 1 the forwarding of packets using MAC learning
        self.add_flow(datapath=datapath, priority=0, command=command, match=match, inst=inst, waiters=waiters, log_action="controller_handling", table_id=0)

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
        except hub.Timeout:
            del waiters_per_datapath[mod.xid]
        except Exception as ex:
            print(f"add_flow exception: {ex}")

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

        self.logger.info("packet in switch %s SRC: %s DST: %s IN_PORT: %s", dpid, src, dst, in_port)
        
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        self.mac_to_port[dpid][src] = in_port

        if eth.ethertype == ether_types.ETH_TYPE_8021Q:
            self.logger.info("Possibly with protocol GOOSE")
            self.logger.info(eth.ethertype)

        # That is GOOSE (0x88B8) in decimal
        if eth.ethertype == 35000:
            self.logger.info("with protocol GOOSE")

        # GOOSE Multicast list allowed comms based on multicast address and switch port that can reach
        # TODO: Maybe need to make this more granular to include also src MAC address?
        goose_list_scenario_1 = {
            # For 651R_2 --> RTAC
            "01:0c:cd:01:00:02" : [10], 
            # For RTAC --> 651R_2
            "01:0c:cd:01:00:01" : [9], 
            # For RTAC --> 787
            "01:0c:cd:01:00:03" : [7],
            # For RTAC --> 451
            "01:0c:cd:01:00:04" : [2],
            
            # Allow also these two even if they do not play any role
            # 451
            "01:0c:cd:01:00:07" : [10],
            # 787
            "01:0c:cd:01:00:08" : [10]
            
            #("01:0c:cd:01:00:01", [10, 5])
            #("01:0c:cd:01:00:01", 16)
        }

        goose_list_scenario_2 = {
            # For 651R_2 --> RTAC
            "01:0c:cd:01:00:02" : [10], 
            
            # For 487B --> RTAC
            "01:0c:cd:01:00:05" : [10],
            # For 351_2 --> RTAC
            "01:0c:cd:01:00:06" : [10],
            
            # For RTAC --> 651R_2
            "01:0c:cd:01:00:01" : [9], 
            # For RTAC --> 787
            "01:0c:cd:01:00:03" : [7],
            # For RTAC --> 451
            "01:0c:cd:01:00:04" : [2],

            # For 451 --> 487B
            "01:0c:cd:01:00:07" : [5],
            # For 487B --> 351_2
            "01:0c:cd:01:00:05" : [3],
            
            #("01:0c:cd:01:00:01", [10, 5])
            #("01:0c:cd:01:00:01", 16)
        }

        #in_goose_list = [tuple for tuple in goose_list if any(dst == i for i in tuple)]

        if self.scenario == 1:
            goose_list = goose_list_scenario_1
        elif self.scenario == 2:
            goose_list = goose_list_scenario_2
            
        in_goose_list = []

        try:
            in_goose_list = goose_list[dst]
            # print(f"GOOSE packet will go to port: {in_goose_list}")
        except KeyError as err:
            print(f"Key Error for key {err} in goose_list")
            # TODO: Return some sort of error and/or log this action

        if in_goose_list:
            match = parser.OFPMatch(eth_src=src, eth_dst=dst)
            actions = []
            command = ofproto.OFPFC_ADD
            waiters = {}

            for port in in_goose_list:
                actions.append(parser.OFPActionOutput(port))

            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
            
            self.add_flow(datapath=datapath, priority=100, command=command, match=match, inst=inst, waiters=waiters, log_action="packet_in", table_id=0, timeout=0)
            
            
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)

            return
        
        # Regular packets learning
        else:
            print("Regular packets...")
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = ofproto.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
            command = ofproto.OFPFC_ADD
            waiters = {}

            # install a flow to avoid packet_in next time
            if out_port != ofproto.OFPP_FLOOD:
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath=datapath, priority=1, command=command, match=match, inst=inst, waiters=waiters, log_action="packet_in", 
                                  table_id=0, timeout=0, buffer_id=msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath=datapath, priority=1, command=command, match=match, inst=inst, waiters=waiters, log_action="packet_in", table_id=0, timeout=0)
                
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                    in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)

            return