from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data_plt = []
multicast_addresses_scenario_1 = [
    "01:0c:cd:01:00:01",
    "...:02",
    "...:03",
    "...:04"
]

for i in range(1, 5):
    data = pd.read_csv("../analysis/security_latencies_0{0}.csv".format(i))
    df = pd.DataFrame(data=data)
    
    sec = [i * 10000 for i in list(df.iloc[:, 1])]

    data_plt.append(sec)


fig, ax = plt.subplots()
plt.xlabel("Multicast Addresses")
plt.ylabel("Seconds")
plt.figure(figsize =(100, 100))
#ax.boxplot(data_dict.values()) # With outliers
ax.boxplot(data_plt,
           patch_artist = True,
           boxprops = dict(facecolor = "lightblue"),
           showfliers=False)
ax.set_xticklabels(multicast_addresses_scenario_1)
# ax.set_xticks(len(multicast_addresses_scenario_1[0]*len(multicast_addresses_scenario_1)))

# Creating plot
# plt.boxplot(final_data)

now = datetime.now()
# fig.savefig(f"box_{now.strftime('%m_%d_%Y-%H:%M:%S')}.png")

fig.savefig(f"test_box_sec.png")


data_plt = []
for i in range(1, 5):
    data = pd.read_csv("../analysis/learning_latencies_0{0}.csv".format(i))
    df = pd.DataFrame(data=data)
    
    sec = [i * 10000 for i in list(df.iloc[:, 1])]

    data_plt.append(sec)


fig, ax = plt.subplots()
plt.xlabel("Multicast Addresses")
plt.ylabel("Seconds")
plt.figure(figsize =(100, 100))
#ax.boxplot(data_dict.values()) # With outliers
ax.boxplot(data_plt,
           patch_artist = True,
           boxprops = dict(facecolor = "green"),
           showfliers=False)
ax.set_xticklabels(multicast_addresses_scenario_1)
# ax.set_xticks(len(multicast_addresses_scenario_1[0]*len(multicast_addresses_scenario_1)))

# Creating plot
# plt.boxplot(final_data)

now = datetime.now()
# fig.savefig(f"box_{now.strftime('%m_%d_%Y-%H:%M:%S')}.png")

fig.savefig(f"test_box_no_sec.png")