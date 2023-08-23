from scapy.all import *
import datetime
import statistics

###############################
# Import SCAPY and ASN1 modules
###############################
from pyasn1.codec.ber import decoder
from pyasn1.codec.ber import encoder
from pyasn1.type import char
from pyasn1.type import tag
from pyasn1.type import univ
from scapy.layers.l2 import Ether
from scapy.layers.l2 import Dot1Q
from scapy.compat import raw
from scapy.all import rdpcap

###############################
# Import Goose module
###############################
# We have to tell script where to find the Goose module in parent directory
# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir)

from goose.goose import GOOSE
from goose.goose import GOOSEPDU
from goose.goose_pdu import AllData
from goose.goose_pdu import Data
from goose.goose_pdu import IECGoosePDU
from goose.goose_pdu import UtcTime

DEBUG = 0   # 0: off 1: Show Goose Payload 2: Full Debug

count = 0
total = 0
start = 0.0
end = 0.0

lst_1_1 = []
lst_1_2 = []

lst_2_1 = []
lst_2_2 = []

lst_3_1 = []
lst_3_2 = []

lst_4_1 = []
lst_4_2 = []


multicast_addresses_scenario_1 = [
    "01:0c:cd:01:00:01",
    "01:0c:cd:01:00:02",
    "01:0c:cd:01:00:03",
    "01:0c:cd:01:00:04"
]

GOOSE_TYPE = 0x88b8
def gooseTest(pkt):
    isGoose = False
    # Test for a Goose Ether Type
    if pkt.haslayer('Dot1Q'):
        if pkt['Dot1Q'].type == GOOSE_TYPE: isGoose = True
    if pkt.haslayer('Ether'):
        if pkt['Ether'].type == GOOSE_TYPE: isGoose = True
    return isGoose

###############################
# Process GOOSE PDU by decoding it with PYASN1
###############################
def goose_pdu_decode(encoded_data):

    # Debugging on
    if DEBUG > 2: 
        from pyasn1 import debug
        debug.setLogger(debug.Debug('all'))

    g = IECGoosePDU().subtype(
        implicitTag=tag.Tag(
            tag.tagClassApplication,
            tag.tagFormatConstructed,
            1
        )
    )
    decoded_data, unprocessed_trail = decoder.decode(
        encoded_data,
        asn1Spec=g
    )
    # This should work, but not sure.
    return decoded_data

# Measure the E2E delay of packets      

def calculate (pcap_1, pcap_2):
    # global total
    # global final_lst

    next_sqNum = 0
    next_stNum = 1

    total = 0
    final_lst = []

    for index, packet in enumerate(PcapReader(pcap_1)):

        if gooseTest(packet):
            # Use SCAPY to parse the Goose header and the Goose PDU header
            d = GOOSE(packet.load)

            # Grab the Goose PDU for processing
            gpdu = d[GOOSEPDU].original

            # Use PYASN1 to parse the Goose PDU
            gd = goose_pdu_decode(gpdu)
            
        
            # NOTE: Had one more packet in the first pcap so we remove the seond one here.    
            # if (index == 0 or index == 1):
            if (index == 1):
                continue

            eth = packet[Ether]
            # TODO: Here we should also record the stNum and sqNum to correlate them later
            # We should also do it for the rest of the multicast addresses.
            if eth.dst == "01:0c:cd:01:00:01":
                # print(gd[6])
                lst_1_1.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:02":
                # if (gd[6] == 0):
                if (index == 0):
                    continue
                 
                lst_2_1.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:03":
                lst_3_1.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:04":
                lst_4_1.append(packet.time)
                total += 1

    print("Total packets of {0}: {1}".format(pcap_1, total))
    
    total = 0

    for index, packet in enumerate(PcapReader(pcap_2)):
        # TODO: Here we should also record the stNum and sqNum to correlate them later
        # We should also do it for the rest of the multicast addresses.

        # if (index == 0):
        #     print("INDEX 0 IS {0}".format(gd[6]))

        # if (index == 1):
        #     print("INDEX 1 IS {0}".format(gd[6]))
        #     continue

        if gooseTest(packet):
            # Use SCAPY to parse the Goose header and the Goose PDU header
            d = GOOSE(packet.load)

            # Grab the Goose PDU for processing
            gpdu = d[GOOSEPDU].original

            # Use PYASN1 to parse the Goose PDU
            gd = goose_pdu_decode(gpdu)

            # NOTE: To fix weird duplicate packet problem, might not needed
            # if (index == 0 or index == 1):
            
            eth = packet[Ether]
            if eth.dst == "01:0c:cd:01:00:01":
                if (index == 0):
                    continue
                lst_1_2.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:02":
                
                # To remove the first packet that does not reach the destination
                # if (gd[6] == 0):
                #     continue
                
                # # To accomodate the changes in StNum
                # if(next_stNum != gd[5]):
                #     next_stNum = gd[5]
                #     next_sqNum = 0

                # if(next_sqNum == gd[6]):
                #     # print("HERE")
                #     next_sqNum += 1     
                #     # print(gd[6])
                #     lst_2_2.append(packet.time)
                
                lst_2_2.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:03":
                lst_3_2.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:04":
                lst_4_2.append(packet.time)
                total += 1

    print("Total packets of {0}: {1}".format(pcap_2, total))

    # if len(lst_1) == len(lst_2):

    print("For {0} and {1} we have the following:".format(pcap_1, pcap_2))

    for index, ts in enumerate(lst_1_1):
        # print("Index {0}".format(index))
        try:
            final_lst.append(ts - lst_1_2[index])
        except IndexError as err:
            # print("Index Error at {0}".format(index))
            continue

   
    print("01:0c:cd:01:00:01")

    if final_lst :

        print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst)))
        print("Standard deviation: {0}".format(statistics.stdev(final_lst)))
        print("Variance: {0}".format(statistics.variance(final_lst)))
        print("Min: {0}".format(min(final_lst)))
        print("Max: {0}".format(max(final_lst)))
        # Is the below correct?
        print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst))/math.sqrt(len(final_lst))))
    
    final_lst = []

    # for index, ts in enumerate(lst_2_1):
    for index, ts in enumerate(lst_2_2):
        # print("Index {0}".format(index))
        try:
            # final_lst.append(ts - lst_2_2[index])
            final_lst.append(ts - lst_2_1[index])
        except IndexError as err:
            # print("Index Error at {0}".format(index))
            continue

   
    print("01:0c:cd:01:00:02")

    if final_lst :
        print("FINAL len {0}".format(len(final_lst)))
        print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst)))
        print("Standard deviation: {0}".format(statistics.stdev(final_lst)))
        print("Variance: {0}".format(statistics.variance(final_lst)))
        print("Min: {0}".format(min(final_lst)))
        print("Max: {0}".format(max(final_lst)))
        # Is the below correct?
        print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst))/math.sqrt(len(final_lst))))
        # print("=======================================")
        # print(final_lst)
    
    final_lst = []

    for index, ts in enumerate(lst_3_1):
        # print("Index {0}".format(index))
        try:
            final_lst.append(ts - lst_3_2[index])
        except IndexError as err:
            # print("Index Error at {0}".format(index))
            continue

   
    print("01:0c:cd:01:00:03")

    if final_lst :

        print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst)))
        print("Standard deviation: {0}".format(statistics.stdev(final_lst)))
        print("Variance: {0}".format(statistics.variance(final_lst)))
        print("Min: {0}".format(min(final_lst)))
        print("Max: {0}".format(max(final_lst)))
        # Is the below correct?
        print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst))/math.sqrt(len(final_lst))))

    final_lst = []

    for index, ts in enumerate(lst_4_1):
        # print("Index {0}".format(index))
        try:
            final_lst.append(ts - lst_4_2[index])
        except IndexError as err:
            # print("Index Error at {0}".format(index))
            continue

   
    print("01:0c:cd:01:00:04")

    if final_lst :

        print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst)))
        print("Standard deviation: {0}".format(statistics.stdev(final_lst)))
        print("Variance: {0}".format(statistics.variance(final_lst)))
        print("Min: {0}".format(min(final_lst)))
        print("Max: {0}".format(max(final_lst)))
        # Is the below correct?
        print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst))/math.sqrt(len(final_lst))))

    return

def main(pcap_1="", pcap_2=""):

    # for i in range(0, 10):
    for i in range(0, 1):
        directory  = "../scenario_1_exp_{0}".format(i)
        pcap_1 = None
        pcap_2 = None

        for index, filename in enumerate(os.listdir(directory)):
            f = os.path.join(directory, filename)
            # checking if it is a file
            if os.path.isfile(f):
                print(f)
                # if (index % 2) == 0:
                #     pcap_1 = f
                # elif (index % 2) != 0:
                #     pcap_2 = f

                #     calculate(pcap_1=pcap_1, pcap_2=pcap_2)

                if (f == "../scenario_1_exp_{0}/exp_{0}_651R_2.pcap".format(i)):
                    pcap_1 = f
                elif (f == "../scenario_1_exp_{0}/exp_{0}_RTAC.pcap".format(i)):
                    pcap_2 = f
                
                if (pcap_1 and pcap_2):
                    calculate(pcap_1=pcap_1, pcap_2=pcap_2)
                    print("===============================")
    
    

    return

if __name__ == '__main__':

    # TODO: These can be taken directly when scanning the whole directory with the pcaps
    # to perform the analysis for all the communication paths.
     
    # pcap_1 = sys.argv[1]
    # pcap_2 = sys.argv[2]

    # main(pcap_1, pcap_2)
    
    main()