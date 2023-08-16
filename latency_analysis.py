from scapy.all import *
import datetime
import statistics

count = 0
total = 0
start = 0.0
end = 0.0
lst_1 = []

lst_2 = []

final_lst = []

# Measure the E2E delay of packets      

def calculate (pcap_1, pcap_2):
    global total
    for index, packet in enumerate(PcapReader(pcap_1)):
        # Had one more packet in the first pcap so we remove the seond one here.    
        if (index == 1):
            continue

        eth = packet[Ether]
        # Here we should also record the stNum and sqNum to correlate them later
        # We should also do it for the rest of the multicast addresses.
        if eth.dst == "01:0c:cd:01:00:01":
            lst_1.append(packet.time)
            total += 1

    print("Total packets of {0}: {1}".format(sys.argv[1], total))
    total = 0

    for packet in PcapReader(pcap_2):
        eth = packet[Ether]
        # Here we should also record the stNum and sqNum to correlate them later
        # We should also do it for the rest of the multicast addresses.
        if eth.dst == "01:0c:cd:01:00:01":
            lst_2.append(packet.time)
            total += 1

    print("Total packets of {0}: {1}".format(sys.argv[2], total))

    # if len(lst_1) == len(lst_2):

    for index, ts in enumerate(lst_1):
        # print("Index {0}".format(index))
        final_lst.append(ts - lst_2[index])

    return

def main(pcap_1, pcap_2):

    calculate(pcap_1=pcap_1, pcap_2=pcap_2)

    print("Average (mean) time between two packets: {0}".format(statistics.mean(final_lst)))
    print("Standard deviation: {0}".format(statistics.stdev(final_lst)))
    print("Variance: {0}".format(statistics.variance(final_lst)))
    print("Min: {0}".format(min(final_lst)))
    print("Max: {0}".format(max(final_lst)))

    return

if __name__ == '__main__':

    pcap_1 = sys.argv[1]
    pcap_2 = sys.argv[2]

    main(pcap_1, pcap_2)