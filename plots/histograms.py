from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics

data_plt = []
for i in range(1, 5):
# for i in range(1, 2):
    data = pd.read_csv("../analysis/security_latencies_0{0}.csv".format(i))
    df = pd.DataFrame(data=data)
    
    # sec = list(df.iloc[:, 1])
    sec = [i * 10000 for i in list(df.iloc[:, 1])]
    max_n = max(sec)
    min_n = min(sec)

    # print(sec)

    # print(max_n)
    # print(min_n)

    # # Creating histogram
    fig, axs = plt.subplots(1, 1,
                            figsize =(10, 7),)
    plt.xlabel("Latency")
    plt.ylabel("Frequency")
    axs.hist(sec, bins=20, range=[min_n, 0.7], edgecolor='black', facecolor='gray', align='mid')
    axs.set_title("01:0c:cd:01:00:0{0}".format(i))
    fig.savefig("test_hist_sec_{0}.png".format(i))

    # print(df["01:0c:cd:01:00:0{0}".format(i)].describe())
    # max = df["01:0c:cd:01:00:0{0}".format(i)].max()
    # min = df["01:0c:cd:01:00:0{0}".format(i)].min()

    # df.plot.hist(bins=10, column=["01:0c:cd:01:00:0{0}".format(i)], range=[min, max])
    # plt.savefig("test_hist_sec_{0}.png".format(i))

for i in range(1, 5):
# for i in range(1, 2):
    data = pd.read_csv("../analysis/learning_latencies_0{0}.csv".format(i))
    df = pd.DataFrame(data=data)
    
    # sec = list(df.iloc[:, 1])
    sec = [i * 10000 for i in list(df.iloc[:, 1])]
    max_n = max(sec)
    min_n = min(sec)

    # print(sec)

    # print(max_n)
    # print(min_n)

    # # Creating histogram
    fig, axs = plt.subplots(1, 1,
                            figsize =(10, 7),)
    plt.xlabel("Latency")
    plt.ylabel("Frequency")
    axs.hist(sec, bins=20, range=[min_n, 0.7], edgecolor='black', facecolor='gray', align='mid')
    axs.set_title("01:0c:cd:01:00:0{0}".format(i))
    fig.savefig("test_hist_no_sec_{0}.png".format(i))