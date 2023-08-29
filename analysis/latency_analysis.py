from scapy.all import *
import datetime
import statistics

import matplotlib.pyplot as plt
import numpy as np
import pandas as pds

import csv 

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


final_lst_01 = []
final_lst_02 = []
final_lst_03 = []
final_lst_04 = []

multicast_addresses_scenario_1 = [
    "01:0c:cd:01:00:01",
    "01:0c:cd:01:00:02",
    "01:0c:cd:01:00:03",
    "01:0c:cd:01:00:04"
]

sec_bars = []
no_sec_bars = []


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

total_arr_1 = []
total_arr_2 = []

def calculate (pcap_1, pcap_2, security=False):
    global final_lst_01 
    global final_lst_02 
    global final_lst_03 
    global final_lst_04


    lst_1_1 = []
    lst_1_2 = []

    lst_2_1 = []
    lst_2_2 = []

    lst_3_1 = []
    lst_3_2 = []

    lst_4_1 = []
    lst_4_2 = []

    next_sqNum = 0
    next_stNum = 1

    total = 0
    final_lst = []

    global total_arr_1
    global total_arr_2

    for index, packet in enumerate(PcapReader(pcap_1)):

        if gooseTest(packet):
            # Use SCAPY to parse the Goose header and the Goose PDU header
            d = GOOSE(packet.load)

            # Grab the Goose PDU for processing
            gpdu = d[GOOSEPDU].original

            # Use PYASN1 to parse the Goose PDU
            gd = goose_pdu_decode(gpdu)

            if (gd[5] == 1 and (gd[6] == 0)):
                continue

            eth = packet[Ether]
            # TODO: Here we should also record the stNum and sqNum to correlate them later
            # We should also do it for the rest of the multicast addresses.
            if eth.dst == "01:0c:cd:01:00:01":
                # if (gd[5] == 1 and (gd[6] == 0)):
                #     continue

                # if (gd[5] == 4 and gd[6] > 14 and security):
                #     break

                # print(gd[6])
                lst_1_1.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:02":
                # if (gd[6] == 0):
                # if (gd[5] == 1 and (gd[6] == 0) and security):
                #     continue
                 
                lst_2_1.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:03":
                
                # TODO: Needs to be fixed.
                # if (gd[5] == 4 and gd[6] > 20):
                #     break

                lst_3_1.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:04":
                # TODO: Needs to be fixed.
                # if (gd[5] == 4 and gd[6] > 20):
                #     break

                lst_4_1.append(packet.time)
                total += 1

    if "651R" in pcap_1:
        print("Total packets of {0}: {1}".format(pcap_1, total))
        total_arr_1.append(total)
    
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

            if (gd[5] == 1 and (gd[6] == 0)):
                continue
            
            eth = packet[Ether]
            if eth.dst == "01:0c:cd:01:00:01":
                # if (gd[5] == 1 and (gd[6] == 0) and security):
                #     continue
               
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
                
                # TODO: Needs to be fixed.
                # if (gd[5] == 1 and (gd[6] == 0 or gd[6] == 1)):
                # if (gd[5] == 1 and (gd[6] == 0) and security):
                #     continue

                lst_3_2.append(packet.time)
                total += 1
            elif eth.dst == "01:0c:cd:01:00:04":
                # TODO: Needs to be fixed.
                # if (gd[5] == 1 and (gd[6] == 0 or gd[6] == 1)):
                # if (gd[5] == 1 and (gd[6] == 0) and security):
                #     continue
                lst_4_2.append(packet.time)
                total += 1

    if "651R" in pcap_1:
        print("Total packets of {0}: {1}".format(pcap_2, total))
        total_arr_2.append(total)

        # print("total_arr_1 {0}".format(total_arr_1))
        # print("total_arr_1 MIN: {0}".format( min(total_arr_1)))

        # print("total_arr_2 {0}".format(total_arr_2))
        # print("total_arr_2 MIN: {0}".format(min(total_arr_2)))

    # if len(lst_1) == len(lst_2):

    # print("For {0} and {1} we have the following:".format(pcap_1, pcap_2))
   

    for index, ts in enumerate(lst_1_1):
        # print("Index {0}".format(index))
        try:
            final_lst_01.append(ts - lst_1_2[index])
        except IndexError as err:
            # print("01:0c:cd:01:00:01 Index Error at {0}".format(index))
            # print("01:0c:cd:01:00:01 lst_1_1 vs lst_1_2 :{0}, {1}".format(len(lst_1_1), len(lst_1_2)))
            continue

    # for index, ts in enumerate(lst_2_1):
    for index, ts in enumerate(lst_2_2):
        # print("Index {0}".format(index))
        try:
            # final_lst.append(ts - lst_2_2[index])
            final_lst_02.append(ts - lst_2_1[index])
        except IndexError as err:
            # print("01:0c:cd:01:00:02 Index Error at {0}".format(index))
            continue


    for index, ts in enumerate(lst_3_1):
        # print("Index {0}".format(index))
        try:
            final_lst_03.append(ts - lst_3_2[index])
        except IndexError as err:
            # print("Index Error at {0}".format(index))
            continue



    for index, ts in enumerate(lst_4_1):
        # print("Index {0}".format(index))
        try:
            final_lst_04.append(ts - lst_4_2[index])
        except IndexError as err:
            # print("Index Error at {0}".format(index))
            continue

    return

def main(pcap_1="", pcap_2=""):

    for j in [0, 1]:

        for i in range(0, 100):
        # for i in range(0, 1):
            if j == 0:
                directory  = "../scenario_1_exp/security_scenario_1_exp_{0}".format(i)
                security = True
            else:
                directory  = "../scenario_1_exp/learning_scenario_1_exp_{0}".format(i)
                security = False
            
            pcap_1 = None
            pcap_2 = None

            # :01 and :02
            pcap_1 = "{0}/exp_{1}_651R_2.pcap".format(directory, i)
            pcap_2 = "{0}/exp_{1}_RTAC.pcap".format(directory, i)
            calculate(pcap_1=pcap_1, pcap_2=pcap_2, security=security)
            print("===============================")

            # :03
            pcap_1 = "{0}/exp_{1}_787_2.pcap".format(directory, i)
            pcap_2 = "{0}/exp_{1}_RTAC.pcap".format(directory, i)
            calculate(pcap_1=pcap_1, pcap_2=pcap_2, security=security)
            print("===============================")

            # :04
            pcap_1 = "{0}/exp_{1}_451_2.pcap".format(directory, i)
            pcap_2 = "{0}/exp_{1}_RTAC.pcap".format(directory, i)
            calculate(pcap_1=pcap_1, pcap_2=pcap_2, security=security)

            print("===============================")

        print("01:0c:cd:01:00:01")

        if final_lst_01 :

            # x = np.arange(start=0, stop=len(final_lst_01), step=1)
            # y = final_lst_01
            
            # plt.plot(x, y)
            # plt.xlabel("Time (sec)") 
            # plt.ylabel("Latency (sec)")
            # plt.title("Any suitable title")
            # # plt.show()
            # plt.savefig("test.png")

            # a = [1, 2, 2.5, 3, 3.5, 4, 5]
            # series = pds.Series(final_lst_01)
            # series = series.astype('float')
            # # Draw a KDE plot

            # series.plot.kde()

            # plt.savefig("test-density.png")
        
            print("FINAL len {0}".format(len(final_lst_01)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_01)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_01)))
            print("Variance: {0}".format(statistics.variance(final_lst_01)))
            print("Min: {0}".format(min(final_lst_01)))
            print("Max: {0}".format(max(final_lst_01)))
            # Is the below correct?
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_01))/math.sqrt(len(final_lst_01))))

        print("01:0c:cd:01:00:02")

        if final_lst_02 :
            print("FINAL len {0}".format(len(final_lst_02)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_02)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_02)))
            print("Variance: {0}".format(statistics.variance(final_lst_02)))
            print("Min: {0}".format(min(final_lst_02)))
            print("Max: {0}".format(max(final_lst_02)))
            # Is the below correct?
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_02))/math.sqrt(len(final_lst_02))))

        print("01:0c:cd:01:00:03")

        if final_lst_03 :
            print("FINAL len {0}".format(len(final_lst_03)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_03)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_03)))
            print("Variance: {0}".format(statistics.variance(final_lst_03)))
            print("Min: {0}".format(min(final_lst_03)))
            print("Max: {0}".format(max(final_lst_03)))
            # Is the below correct?
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_03))/math.sqrt(len(final_lst_03))))

        print("01:0c:cd:01:00:04")

        if final_lst_04 :
            print("FINAL len {0}".format(len(final_lst_04)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_04)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_04)))
            print("Variance: {0}".format(statistics.variance(final_lst_04)))
            print("Min: {0}".format(min(final_lst_04)))
            print("Max: {0}".format(max(final_lst_04)))
            # Is the below correct?
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_04))/math.sqrt(len(final_lst_04))))


        # field names 
        fields = ['Address', 'Mean-E2E_Latency'] 
            
        # data rows of csv file 
        rows = [ ['01:0c:cd:01:00:01', statistics.mean(final_lst_01)], 
                ['01:0c:cd:01:00:02', statistics.mean(final_lst_02)], 
                ['01:0c:cd:01:00:03', statistics.mean(final_lst_03)], 
                ['01:0c:cd:01:00:04', statistics.mean(final_lst_04)]
            ]
            
        if(security):
            sec_bars = [statistics.mean(final_lst_01), statistics.mean(final_lst_02), statistics.mean(final_lst_03), statistics.mean(final_lst_04)]
            sec_bars = [i * 1000 for i in sec_bars]
                
            # name of csv file 
            filename = "security_results.csv"
                
          
        else:
            no_sec_bars = [statistics.mean(final_lst_01), statistics.mean(final_lst_02), statistics.mean(final_lst_03), statistics.mean(final_lst_04)]
            no_sec_bars = [i * 1000 for i in no_sec_bars]

            # name of csv file 
            filename = "learning_results.csv"
        
        # writing to csv file 
        with open(filename, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(rows)
            
    # # set width of bar
    # barWidth = 0.3
    # fig = plt.subplots(figsize =(12, 8))

    # ind = np.arange(len(multicast_addresses_scenario_1))

    #  # Make the plot
    # plt.bar(ind, sec_bars, color ='b', width = barWidth,
    #         label ='Mean Time (w/ security)')
    # plt.bar(ind+barWidth, no_sec_bars, color ='g', width = barWidth,
    #         label ='Mean Time (w/o security)')
    
    # # Adding Xticks
    # plt.xlabel('Multicast Addresses', fontweight ='bold', fontsize = 15)
    # plt.ylabel('Mean E2E latency (ms)', fontweight ='bold', fontsize = 15)
    # plt.xticks(ind + barWidth / 2, multicast_addresses_scenario_1)
    
    # plt.legend()

    # plt.savefig("test-bar.png")

    return

if __name__ == '__main__':

    # TODO: These can be taken directly when scanning the whole directory with the pcaps
    # to perform the analysis for all the communication paths.
     
    # pcap_1 = sys.argv[1]
    # pcap_2 = sys.argv[2]

    # main(pcap_1, pcap_2)
    
    main()
