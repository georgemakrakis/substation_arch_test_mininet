from scapy.all import *
import datetime

count = 0
total = 0
start = 0.0
end = 0.0
lst_1 = []

lst_2 = []

final_lst = []

# Measure the E2E delay of packets      


for index, packet in enumerate(PcapReader(sys.argv[1])):
    # Had one more packet in the first pcap so we remove the seond one here.    
    if (index == 1):
        continue

    eth = packet[Ether]
    # Here we should also record the stNum and sqNum to correlate them later
    if eth.dst == "01:0c:cd:01:00:01":
        lst_1.append(packet.time)
        total += 1

print("Total packets of {0}: {1}".format(sys.argv[1], total))
total = 0

for packet in PcapReader(sys.argv[2]):
    eth = packet[Ether]
    # Here we should also record the stNum and sqNum to correlate them later
    if eth.dst == "01:0c:cd:01:00:01":
        lst_2.append(packet.time)
        total += 1

print("Total packets of {0}: {1}".format(sys.argv[2], total))

# if len(lst_1) == len(lst_2):

for index, ts in enumerate(lst_1):
    # print("Index {0}".format(index))
    final_lst.append(ts - lst_2[index])

# for item in lst:
#    print(item)
print("Average time between two packets: ", sum(final_lst) / len(final_lst))
