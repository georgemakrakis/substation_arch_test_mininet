import json
import socket
from ryu.base import app_manager # This is the main entry point for the controller application.

from ryu.controller import ofp_event # To capture openflow event, when the openflow packet received
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, HANDSHAKE_DISPATCHER
from ryu.controller.handler import set_ev_cls

from ryu.ofproto import ofproto_v1_3  # Specify the Openflow version to be used.


from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import ether_types

from ryu.lib import hub
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from webob import Response


simple_app_instance_name = 'simple_app'
urlStatsAll = '/processBus/getStats/{tableId}/{inPort}'

OFP_REPLY_TIMER = 1.0  # sec

class SEL_2740S(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SEL_2740S, self).__init__(*args, **kwargs)
        # DATAPATH_ID:00000030a71cca39
        # self.datapaths = ["00000030a71cca39"]
        self.datapaths = []
        self.mac_to_port = {} # The mac address table is empty initially.

        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.bind(('0.0.0.0', 31415))
        # sock.connect(("172.20.20.102", 6653))

        wsgi = kwargs['wsgi']
        self.datapath = None
        self.flows_stats = []
        self.group_stats = []
        wsgi.register(SEL_2740S_Ryu_Controller,
                      {simple_app_instance_name: self})


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        print(f"New Datapath {datapath}")
        self.datapaths.append(datapath)

        print("DATAPATH ID: ", datapath.id)

        self.datapath = datapath

        # Install the table-miss flow entry
        # match = parser.OFPMatch()

        # actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
        #                                   ofproto.OFPCML_NO_BUFFER)]
        # self.add_flow(datapath, 0, match, actions)

        # Delete the flow if it exists initially
        priority = 1
        match = parser.OFPMatch(in_port=13)
        actions = [parser.OFPActionOutput(16)]
        # inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
        #                                      actions)]
        
        # flow_del_request = parser.OFPFlowMod(datapath=datapath,
        #                                     command=ofproto.OFPFC_DELETE,
        #                                     priority = priority,
        #                                     instructions=inst,
        #                                     match=match,
        #                                     table_id=0)
        # datapath.send_msg(flow_del_request)

        priority=1
        table_id=0
        instructions = []
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath, 
                                                      0, 
                                                      0, 
                                                      table_id, 
                                                      ofproto.OFPFC_DELETE, 
                                                      0, 
                                                      0, 
                                                      priority,
                                                      ofproto.OFPCML_NO_BUFFER,  
                                                      ofproto.OFPP_ANY, 
                                                      ofproto.OFPG_ANY, 
                                                      0, 
                                                      match, 
                                                      instructions)
        datapath.send_msg(flow_mod)

        match = parser.OFPMatch(in_port=16)
        priority=1
        table_id=0
        instructions = []
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath, 
                                                      0, 
                                                      0, 
                                                      table_id, 
                                                      ofproto.OFPFC_DELETE, 
                                                      0, 
                                                      0, 
                                                      priority,
                                                      ofproto.OFPCML_NO_BUFFER,  
                                                      ofproto.OFPP_ANY, 
                                                      ofproto.OFPG_ANY, 
                                                      0, 
                                                      match, 
                                                      instructions)
        datapath.send_msg(flow_mod)


        # match = parser.OFPMatch(in_port=16)
        # actions = [parser.OFPActionOutput(13)]
        # flow_del_request = parser.OFPFlowMod(datapath=datapath,
        #                                     command=ofproto.OFPFC_DELETE,
        #                                     priority = priority,
        #                                     instructions=inst,
        #                                     match=match,
        #                                     table_id=0)
        # datapath.send_msg(flow_del_request)

        
        # Then add...

        # match = parser.OFPMatch(in_port=13)
        # actions = [parser.OFPActionOutput(16)]
        # self.add_flow(datapath, 1, match, actions)

        # match = parser.OFPMatch(in_port=16)
        # actions = [parser.OFPActionOutput(13)]
        # self.add_flow(datapath, 1, match, actions)

    def remove_table_flows(self, datapath, table_id, match, instructions):
        """Create OFP flow mod message to remove flows from table."""
        ofproto = datapath.ofproto
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath, 0, 0, table_id, ofproto.OFPFC_DELETE, 0, 0, 1, ofproto.OFPCML_NO_BUFFER,  ofproto.OFPP_ANY, ofproto.OFPG_ANY, 0, match, instructions)
        return flow_mod

    def del_all_flows (self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
    
        empty_match = parser.OFPMatch()
        instructions = []
        flow_mod = self.remove_table_flows(datapath, 0,
                                        empty_match, instructions)
        
        print("deleting all flow entries in table 0")
        datapath.send_msg(flow_mod)

    def add_flow(self, datapath, priority, match, actions, table_id=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Construct flow message and send it.
        # inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_WRITE_ACTIONS ,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, table_id=table_id, instructions=inst)
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

        self.logger.info("packet in switch %s SRC: %s DST: %s IN_PORT: %s", dpid, src, dst, in_port)
        if eth_pkt.ethertype == ether_types.ETH_TYPE_ARP:
            self.logger.info("with protocol ARP")

        # Learn a mac address so next time the packet will not be flooded
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            print("Found!!!")
            out_port = self.mac_to_port[dpid][dst]
        else:
            print("Flooding...")
            out_port = ofproto.OFPP_FLOOD

        # The actions list
        actions = [parser.OFPActionOutput(out_port)]

        # Install a flow to the switch to avoid packet_in to controller next time.
        if out_port != ofproto.OFPP_FLOOD:
            print("Not Flood, adding new flow!!!")
            match = parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath, 1, match, actions, 0)

        # Construct packet_out to switch message and send it
        out = parser.OFPPacketOut(datapath=datapath,
                                buffer_id=ofproto.OFP_NO_BUFFER,
                                in_port=in_port, actions=actions,
                                data=msg.data)
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


    def send_flow_stats_request(self, datapath, in_port, waiters, table_id):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        cookie = cookie_mask = 0

        match = ofp_parser.OFPMatch() 
        table_id_int = None

       
        try:
            in_port_int = int(in_port)
            match = ofp_parser.OFPMatch()

            table_id_int = int(table_id)
            
            if in_port_int != 0:
                # match = ofp_parser.OFPMatch(in_port=in_port_int)
                match = ofp_parser.OFPMatch(in_port=in_port_int)
            else:
                print(f"Port 0 for table {table_id_int} requested")
                match = ofp_parser.OFPMatch()
        except ValueError as er:
            print("The provided in_port or table_id is not a number")
            return -1
        
        # req = ofp_parser.OFPFlowStatsRequest(datapath, table_id_int,
        req = ofp_parser.OFPFlowStatsRequest(datapath, 0,
                                            table_id_int,
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

class SEL_2740S_Ryu_Controller(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(SEL_2740S_Ryu_Controller, self).__init__(req, link, data, **config)
        self.simple_app = data[simple_app_instance_name]

    @route('processBus', urlStatsAll, methods=['GET'])
    def get_flow_stats(self, req, **kwargs):
        datapath = self.simple_app.datapath
        table_id = kwargs['tableId']
        in_port = kwargs['inPort']

        waiters = {}
        
        self.simple_app.send_flow_stats_request(datapath, in_port, waiters, table_id)

        simple_app = self.simple_app
        flows_stats = simple_app.flows_stats

        # ... and then for the regular flow handling
        # table_id = 1

        # self.process_bus_app.send_flow_stats_request(datapath, in_port, waiters, table_id)

        # process_bus_app = self.process_bus_app
        # flows_stats += process_bus_app.flows_stats

        body = json.dumps(flows_stats)
        simple_app.flows_stats = []

        return Response(content_type='text/json', body=body)
        # return Response(content_type='text/plain', body="OK\n")

