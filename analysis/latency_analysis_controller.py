from pathlib import Path
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

lst_5_1 = []
lst_5_2 = []

lst_6_1 = []
lst_6_2 = []

lst_9_1 = []
lst_9_2 = []

lst_10_1 = []
lst_10_2 = []


final_lst_01 = []
final_lst_02 = []
final_lst_03 = []
final_lst_04 = []
final_lst_05 = []
final_lst_06 = []
final_lst_09 = []
final_lst_10 = []

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
    global final_lst_05
    global final_lst_06
    global final_lst_09
    global final_lst_10


    lst_1_1 = []
    lst_1_2 = []

    lst_2_1 = []
    lst_2_2 = []

    lst_3_1 = []
    lst_3_2 = []

    lst_4_1 = []
    lst_4_2 = []

    lst_5_1 = []
    lst_5_2 = []

    lst_6_1 = []
    lst_6_2 = []

    lst_9_1 = []
    lst_9_2 = []

    lst_10_1 = []
    lst_10_2 = []

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


                eth = packet[Ether]
                if eth.dst == "01:0c:cd:01:00:01":

                    lst_1_1.append(packet.time)
                    total += 1
                elif eth.dst == "01:0c:cd:01:00:02":

                    lst_2_1.append(packet.time)
                    total += 1
                elif eth.dst == "01:0c:cd:01:00:03":

                    lst_3_1.append(packet.time)
                    total += 1
                elif eth.dst == "01:0c:cd:01:00:04":

                    lst_4_1.append(packet.time)
                    total += 1
                elif eth.dst == "01:0c:cd:01:00:05":

                    lst_5_1.append(packet.time)
                    total += 1
                elif eth.dst == "01:0c:cd:01:00:06":

                    lst_6_1.append(packet.time)
                    total += 1

                elif eth.dst == "01:0c:cd:01:00:09":

                    lst_9_1.append(packet.time)
                    total += 1

                elif eth.dst == "01:0c:cd:01:00:10":

                    lst_10_1.append(packet.time)
                    total += 1


    total = 0

    for index, packet in enumerate(PcapReader(pcap_2)):

        # if gooseTest(packet) and index > 10:
        if gooseTest(packet):
            # Use SCAPY to parse the Goose header and the Goose PDU header
            d = GOOSE(packet.load)

            # Grab the Goose PDU for processing
            gpdu = d[GOOSEPDU].original

            # Use PYASN1 to parse the Goose PDU
            gd = goose_pdu_decode(gpdu)

            if (gd[5] == 1 and (gd[6] == 0)):


                eth = packet[Ether]
                if eth.dst == "01:0c:cd:01:00:01":
                    lst_1_2.append(packet.time)
                    total += 1
                elif eth.dst == "01:0c:cd:01:00:02":
                    lst_2_2.append(packet.time)
                    total += 1
                elif eth.dst == "01:0c:cd:01:00:03":
                    lst_3_2.append(packet.time)
                    total += 1
                elif eth.dst == "01:0c:cd:01:00:04":
                    lst_4_2.append(packet.time)
                    total += 1

                elif eth.dst == "01:0c:cd:01:00:05":

                    lst_5_2.append(packet.time)
                    total += 1
                elif eth.dst == "01:0c:cd:01:00:06":

                    lst_6_2.append(packet.time)
                    total += 1

                elif eth.dst == "01:0c:cd:01:00:09":

                    lst_9_2.append(packet.time)
                    total += 1

                elif eth.dst == "01:0c:cd:01:00:10":

                    lst_10_2.append(packet.time)
                    total += 1

    for index, ts in enumerate(lst_1_1):
        try:
            final_lst_01.append(ts - lst_1_2[index])
        except IndexError as err:
            continue

    for index, ts in enumerate(lst_2_2):
        try:
            final_lst_02.append(ts - lst_2_1[index])
        except IndexError as err:
            continue


    for index, ts in enumerate(lst_3_1):
        try:
            final_lst_03.append(ts - lst_3_2[index])
        except IndexError as err:
            continue

    for index, ts in enumerate(lst_4_1):
        try:
            final_lst_04.append(ts - lst_4_2[index])
        except IndexError as err:
            continue


    for index, ts in enumerate(lst_5_1):
        try:
            final_lst_05.append(ts - lst_5_2[index])
        except IndexError as err:
            continue

    for index, ts in enumerate(lst_6_1):
        try:
            final_lst_06.append(ts - lst_6_2[index])
        except IndexError as err:
            continue

    for index, ts in enumerate(lst_9_1):
        try:
            final_lst_09.append(ts - lst_9_2[index])
        except IndexError as err:
            continue

    for index, ts in enumerate(lst_10_1):
        try:
            final_lst_10.append(ts - lst_10_2[index])
        except IndexError as err:
            continue

    return

def main(pcap_1="", pcap_2=""):

    scenario = 1
    # scenario = 2

    # for j in [0, 2]:
    # for j in range(0,1):
    for j in range(1,2):

        for i in range(0, 1000):
        # for i in range(0, 200):

            if j == 0:
                if scenario == 1:
                    directory  = "security/1000/security_scenario_1_exp_{0}".format(i)
                    # directory  = "security/200/security_scenario_1_exp_{0}".format(i)
                elif scenario == 2:
                    directory  = "security/1000/security_scenario_2_exp_{0}".format(i)
                    # directory  = "security/200/security_scenario_2_exp_{0}".format(i)

                security = True
                print("Security {0} ".format(i))
            elif j == 1:
                if scenario == 1:
                    directory  = "learning/1000/learning_scenario_1_exp_{0}".format(i)
                    # directory  = "learning/200/learning_scenario_1_exp_{0}".format(i)
                elif scenario == 2:
                    directory  = "learning/1000/learning_scenario_2_exp_{0}".format(i)
                    # directory  = "learning/200/learning_scenario_2_exp_{0}".format(i)

                security = False
                print("Learning {0}".format(i))
            else:
                return

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

            if scenario == 2:

                # :05
                pcap_1 = "{0}/exp_{1}_487B_2.pcap".format(directory, i)
                pcap_2 = "{0}/exp_{1}_RTAC.pcap".format(directory, i)
                calculate(pcap_1=pcap_1, pcap_2=pcap_2, security=security)

                print("===============================")

                # :06
                pcap_1 = "{0}/exp_{1}_351_2.pcap".format(directory, i)
                pcap_2 = "{0}/exp_{1}_RTAC.pcap".format(directory, i)
                calculate(pcap_1=pcap_1, pcap_2=pcap_2, security=security)

                print("===============================")

                # :09
                pcap_1 = "{0}/exp_{1}_487B_2.pcap".format(directory, i)
                pcap_2 = "{0}/exp_{1}_451_2.pcap".format(directory, i)
                calculate(pcap_1=pcap_1, pcap_2=pcap_2, security=security)

                print("===============================")

                # # :10
                pcap_1 = "{0}/exp_{1}_351_2.pcap".format(directory, i)
                pcap_2 = "{0}/exp_{1}_487B_2.pcap".format(directory, i)
                calculate(pcap_1=pcap_1, pcap_2=pcap_2, security=security)

                print("===============================")


        print("01:0c:cd:01:00:01")

        if final_lst_01 :

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
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_02))/math.sqrt(len(final_lst_02))))

        print("01:0c:cd:01:00:03")

        if final_lst_03 :
            print("FINAL len {0}".format(len(final_lst_03)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_03)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_03)))
            print("Variance: {0}".format(statistics.variance(final_lst_03)))
            print("Min: {0}".format(min(final_lst_03)))
            print("Max: {0}".format(max(final_lst_03)))
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_03))/math.sqrt(len(final_lst_03))))

        print("01:0c:cd:01:00:04")

        if final_lst_04 :
            print("FINAL len {0}".format(len(final_lst_04)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_04)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_04)))
            print("Variance: {0}".format(statistics.variance(final_lst_04)))
            print("Min: {0}".format(min(final_lst_04)))
            print("Max: {0}".format(max(final_lst_04)))
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_04))/math.sqrt(len(final_lst_04))))

        print("01:0c:cd:01:00:05")

        if final_lst_05 :
            print("FINAL len {0}".format(len(final_lst_05)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_05)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_05)))
            print("Variance: {0}".format(statistics.variance(final_lst_05)))
            print("Min: {0}".format(min(final_lst_05)))
            print("Max: {0}".format(max(final_lst_05)))
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_05))/math.sqrt(len(final_lst_05))))

        print("01:0c:cd:01:00:06")

        if final_lst_06 :
            print("FINAL len {0}".format(len(final_lst_06)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_06)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_06)))
            print("Variance: {0}".format(statistics.variance(final_lst_06)))
            print("Min: {0}".format(min(final_lst_06)))
            print("Max: {0}".format(max(final_lst_06)))
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_06))/math.sqrt(len(final_lst_06))))

        print("01:0c:cd:01:00:09")

        if final_lst_09 :

            print("FINAL len {0}".format(len(final_lst_09)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_09)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_09)))
            print("Variance: {0}".format(statistics.variance(final_lst_09)))
            print("Min: {0}".format(min(final_lst_09)))
            print("Max: {0}".format(max(final_lst_09)))
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_09))/math.sqrt(len(final_lst_09))))


        print("01:0c:cd:01:00:10")

        if final_lst_10 :
            print("FINAL len {0}".format(len(final_lst_10)))
            print("Average (mean) E2E delay: {0}".format(statistics.mean(final_lst_10)))
            print("Standard deviation: {0}".format(statistics.stdev(final_lst_10)))
            print("Variance: {0}".format(statistics.variance(final_lst_10)))
            print("Min: {0}".format(min(final_lst_10)))
            print("Max: {0}".format(max(final_lst_10)))
            # Is the below correct?
            print("Standard error of the mean {0}".format(float(statistics.stdev(final_lst_10))/math.sqrt(len(final_lst_10))))

        prefix = ""

        if scenario == 1:
            # prefix = "scenario_1_CSVs"
            prefix = "scenario_1_CSVs_1000"
            print("MAX AVG Latency {0}".format(max([abs(statistics.mean(final_lst_01)), abs(statistics.mean(final_lst_02)), abs(statistics.mean(final_lst_03)), abs(statistics.mean(final_lst_04))])))
            print("MIN AVG Latency {0}".format(min([abs(statistics.mean(final_lst_01)), abs(statistics.mean(final_lst_02)), abs(statistics.mean(final_lst_03)), abs(statistics.mean(final_lst_04))])))
        elif scenario == 2:
            # prefix = "scenario_2_CSVs"
            prefix = "scenario_2_CSVs_1000"
            print("MAX AVG Latency {0}".format(max([abs(statistics.mean(final_lst_01)), abs(statistics.mean(final_lst_02)), abs(statistics.mean(final_lst_03)), abs(statistics.mean(final_lst_04)), abs(statistics.mean(final_lst_05)), abs(statistics.mean(final_lst_06)), abs(statistics.mean(final_lst_09)), abs(statistics.mean(final_lst_10))])))
            print("MIN AVG Latency {0}".format(min([abs(statistics.mean(final_lst_01)), abs(statistics.mean(final_lst_02)), abs(statistics.mean(final_lst_03)), abs(statistics.mean(final_lst_04)), abs(statistics.mean(final_lst_05)), abs(statistics.mean(final_lst_06)), abs(statistics.mean(final_lst_09)), abs(statistics.mean(final_lst_10))])))


        # field names
        fields = ["Address", "Mean-E2E_Latency"]

        # data rows of csv file
        rows = [ ["01:0c:cd:01:00:01", statistics.mean(final_lst_01)],
                ["01:0c:cd:01:00:02", statistics.mean(final_lst_02)],
                ["01:0c:cd:01:00:03", statistics.mean(final_lst_03)],
                ["01:0c:cd:01:00:04", statistics.mean(final_lst_04)]
            ]

        if(final_lst_05 and final_lst_06 and final_lst_09 and final_lst_10):
            # data rows of csv file
            rows = [ ["01:0c:cd:01:00:01", statistics.mean(final_lst_01)],
                    ["01:0c:cd:01:00:02", statistics.mean(final_lst_02)],
                    ["01:0c:cd:01:00:03", statistics.mean(final_lst_03)],
                    ["01:0c:cd:01:00:04", statistics.mean(final_lst_04)],
                    ["01:0c:cd:01:00:05", statistics.mean(final_lst_05)],
                    ["01:0c:cd:01:00:06", statistics.mean(final_lst_06)],
                    ["01:0c:cd:01:00:09", statistics.mean(final_lst_09)],
                    ["01:0c:cd:01:00:10", statistics.mean(final_lst_10)],
                ]

        if(security):
            sec_bars = [statistics.mean(final_lst_01), statistics.mean(final_lst_02), statistics.mean(final_lst_03), statistics.mean(final_lst_04)]
            sec_bars = [i * 1000 for i in sec_bars]

            # name of csv file
            filename = "{0}/security_results_controller.csv".format(prefix)

            if(final_lst_05 and final_lst_06 and final_lst_09 and final_lst_10):
                sec_bars = [statistics.mean(final_lst_01), statistics.mean(final_lst_02), statistics.mean(final_lst_03), statistics.mean(final_lst_04),
                            statistics.mean(final_lst_05), statistics.mean(final_lst_06), statistics.mean(final_lst_09), statistics.mean(final_lst_10)]
                sec_bars = [i * 1000 for i in sec_bars]

                filename = "{0}/security_results_controller_scenario_2.csv".format(prefix)


        else:
            no_sec_bars = [statistics.mean(final_lst_01), statistics.mean(final_lst_02), statistics.mean(final_lst_03), statistics.mean(final_lst_04)]
            no_sec_bars = [i * 1000 for i in no_sec_bars]

            # name of csv file
            filename = "{0}/learning_results_controller.csv".format(prefix)

            if(final_lst_05 and final_lst_06 and final_lst_09 and final_lst_10):
                no_sec_bars = [statistics.mean(final_lst_01), statistics.mean(final_lst_02), statistics.mean(final_lst_03), statistics.mean(final_lst_04),
                            statistics.mean(final_lst_05), statistics.mean(final_lst_06), statistics.mean(final_lst_09), statistics.mean(final_lst_10)]
                no_sec_bars = [i * 1000 for i in no_sec_bars]

                filename = "{0}/learning_results_controller_scenario_2.csv".format(prefix)

        # writing to csv file
        with open(filename, "w") as csvfile:
            csvwriter = csv.writer(csvfile)

            csvwriter.writerow(fields)

            csvwriter.writerows(rows)


        # ================================\
        if(security):
            df = pds.DataFrame([], columns=["01:0c:cd:01:00:01"])
            df["01:0c:cd:01:00:01"] = final_lst_01
            filepath = Path('./{0}/control_security_latencies_01.csv'.format(prefix))
            df.to_csv(filepath)

            df = pds.DataFrame([], columns=["01:0c:cd:01:00:02"])
            df["01:0c:cd:01:00:02"] = final_lst_02
            filepath = Path('./{0}/control_security_latencies_02.csv'.format(prefix))
            df.to_csv(filepath)

            df = pds.DataFrame([], columns=["01:0c:cd:01:00:03"])
            df["01:0c:cd:01:00:03"] = final_lst_03
            filepath = Path('./{0}/control_security_latencies_03.csv'.format(prefix))
            df.to_csv(filepath)

            df = pds.DataFrame([], columns=["01:0c:cd:01:00:04"])
            df["01:0c:cd:01:00:04"] = final_lst_04
            filepath = Path('./{0}/control_security_latencies_04.csv'.format(prefix))
            df.to_csv(filepath)

            if(final_lst_05 and final_lst_06 and final_lst_09 and final_lst_10):
                df = pds.DataFrame([], columns=["01:0c:cd:01:00:05"])
                df["01:0c:cd:01:00:05"] = final_lst_05
                filepath = Path('./{0}/control_security_latencies_05.csv'.format(prefix))
                df.to_csv(filepath)

                df = pds.DataFrame([], columns=["01:0c:cd:01:00:06"])
                df["01:0c:cd:01:00:06"] = final_lst_06
                filepath = Path('./{0}/control_security_latencies_06.csv'.format(prefix))
                df.to_csv(filepath)

                df = pds.DataFrame([], columns=["01:0c:cd:01:00:09"])
                df["01:0c:cd:01:00:09"] = final_lst_09
                filepath = Path('./{0}/control_security_latencies_09.csv'.format(prefix))
                df.to_csv(filepath)

                df = pds.DataFrame([], columns=["01:0c:cd:01:00:10"])
                df["01:0c:cd:01:00:10"] = final_lst_10
                filepath = Path('./{0}/control_security_latencies_10.csv'.format(prefix))
                df.to_csv(filepath)

        else:
            df = pds.DataFrame([], columns=["01:0c:cd:01:00:01"])
            df["01:0c:cd:01:00:01"] = final_lst_01
            filepath = Path('./{0}/control_learning_latencies_01.csv'.format(prefix))
            df.to_csv(filepath)

            df = pds.DataFrame([], columns=["01:0c:cd:01:00:02"])
            df["01:0c:cd:01:00:02"] = final_lst_02
            filepath = Path('./{0}/control_learning_latencies_02.csv'.format(prefix))
            df.to_csv(filepath)

            df = pds.DataFrame([], columns=["01:0c:cd:01:00:03"])
            df["01:0c:cd:01:00:03"] = final_lst_03
            filepath = Path('./{0}/control_learning_latencies_03.csv'.format(prefix))
            df.to_csv(filepath)

            df = pds.DataFrame([], columns=["01:0c:cd:01:00:04"])
            df["01:0c:cd:01:00:04"] = final_lst_04
            filepath = Path('./{0}/control_learning_latencies_04.csv'.format(prefix))
            df.to_csv(filepath)

            if(final_lst_05 and final_lst_06 and final_lst_09 and final_lst_10):
                df = pds.DataFrame([], columns=["01:0c:cd:01:00:05"])
                df["01:0c:cd:01:00:05"] = final_lst_05
                filepath = Path('./{0}/control_learning_latencies_05.csv'.format(prefix))
                df.to_csv(filepath)

                df = pds.DataFrame([], columns=["01:0c:cd:01:00:06"])
                df["01:0c:cd:01:00:06"] = final_lst_06
                filepath = Path('./{0}/control_learning_latencies_06.csv'.format(prefix))
                df.to_csv(filepath)

                df = pds.DataFrame([], columns=["01:0c:cd:01:00:09"])
                df["01:0c:cd:01:00:09"] = final_lst_09
                filepath = Path('./{0}/control_learning_latencies_09.csv'.format(prefix))
                df.to_csv(filepath)

                df = pds.DataFrame([], columns=["01:0c:cd:01:00:10"])
                df["01:0c:cd:01:00:10"] = final_lst_10
                filepath = Path('./{0}/control_learning_latencies_10.csv'.format(prefix))
                df.to_csv(filepath)

    return

if __name__ == '__main__':

    main()
