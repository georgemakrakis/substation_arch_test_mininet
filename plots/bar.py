import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# set width of bar
barWidth = 0.3
fig = plt.subplots(figsize =(12, 8))

data = pd.read_csv("../analysis/security_results.csv")
df = pd.DataFrame(data=data)
  
multicast_addresses_scenario_1 = list(df.iloc[:, 0])
sec_bars = [i * 10000 for i in list(df.iloc[:, 1])]

ind = np.arange(len(multicast_addresses_scenario_1))

plt.bar(ind, sec_bars, color ="b", width = barWidth,
    label ="Mean Time (w/ security)")

data = pd.read_csv("../analysis/learning_results.csv")
df = pd.DataFrame(data=data)
  
multicast_addresses_scenario_1 = list(df.iloc[:, 0])
no_sec_bars = [i * 10000 for i in list(df.iloc[:, 1])]


plt.bar(ind+barWidth, no_sec_bars, color ="g", width = barWidth,
        label ="Mean Time (w/o security)")

# Adding Xticks
plt.xlabel("Multicast Addresses", fontweight ="bold", fontsize = 15)
plt.ylabel("Mean E2E latency (ms)", fontweight ="bold", fontsize = 15)
plt.xticks(ind + barWidth / 2, multicast_addresses_scenario_1)

plt.legend()

plt.savefig("test-bar.png")