from scapy.all import *
import goose

a = rdpcap("./goose_CHE_203_generic/scenario1_test_RTAC.pcap")
for i in a:
    try:
        if i.type == 0x88b8:
            g = goose.GOOSE(i.load)
            print(repr(g.load))
            gpdu = goose.GOOSEPDU(g.load[4:])
            print(gpdu.__dict__)
        if i.type == 0x8100:
            
            pkt = i[Dot1Q].payload

            g = goose.GOOSE(pkt)
            print(repr(g.load))
            gpdu = goose.GOOSEPDU(g.load[4:])
            print(gpdu.__dict__)

    except AttributeError:
        continue