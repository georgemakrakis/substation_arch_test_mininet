from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics


def main (security):

    if security:
        prefix = "../1000/security_latencies_0"
        title = "With Security"
        now = datetime.now()
        final_name = f"hist_sec_{now.strftime('%m_%d_%Y-%H_%M_%S')}.png"
    else:
        prefix = "../1000/learning_latencies_0"
        title = "Without Security"
        now = datetime.now()
        final_name = f"hist_no_sec_{now.strftime('%m_%d_%Y-%H_%M_%S')}.png"


    data_plt = []

    colors = ["red", "green", "blue", "gray"]
    # # Creating histogram
    fig, axs = plt.subplots(1, 1,
                        figsize =(10, 7),)

    for i in range(1, 5):
    # for i in range(1, 2):
        data = pd.read_csv("{0}{1}.csv".format(prefix,i))
        df = pd.DataFrame(data=data)
        
        # sec = list(df.iloc[:, 1])
        sec = [i * 10000 for i in list(df.iloc[:, 1])]
        max_n = max(sec)
        min_n = min(sec)

        # print(sec)

        # print(max_n)
        # print(min_n)

        plt.xlabel("Latency")
        plt.ylabel("Frequency")
        
        
        plt.hist(sec, bins=20, range=[min_n, 0.7], edgecolor="black", alpha=0.5, facecolor=colors[i-1], align="mid", label="01:0c:cd:01:00:0{0}".format(i))
        
        # axs.hist(sec, bins=20, range=[min_n, 0.7], edgecolor="black", facecolor=colors[i-1], align="mid", label="01:0c:cd:01:00:0{0}".format(i))
        # axs.set_title("01:0c:cd:01:00:0{0}".format(i))
        # fig.savefig("test_hist_sec_{0}.png".format(i))

        # print(df["01:0c:cd:01:00:0{0}".format(i)].describe())
        # max = df["01:0c:cd:01:00:0{0}".format(i)].max()
        # min = df["01:0c:cd:01:00:0{0}".format(i)].min()

        # df.plot.hist(bins=10, column=["01:0c:cd:01:00:0{0}".format(i)], range=[min, max])
        # plt.savefig("test_hist_sec_{0}.png".format(i))

    plt.legend(loc="upper right")
    now = datetime.now()
    axs.set_title(title)
    # fig.savefig("test_hist_sec_{0}.png".format(i))
    fig.savefig(final_name)
    return


# fig, axs = plt.subplots(1, 1,
#                 figsize =(10, 7),)
# for i in range(1, 5):
# # for i in range(1, 2):
#     data = pd.read_csv("../analysis/100_learning_latencies_0{0}.csv".format(i))    
#     df = pd.DataFrame(data=data)
    
#     # sec = list(df.iloc[:, 1])
#     sec = [i * 10000 for i in list(df.iloc[:, 1])]
#     max_n = max(sec)
#     min_n = min(sec)

#     # print(sec)

#     # print(max_n)
#     # print(min_n)

#     plt.xlabel("Latency")
#     plt.ylabel("Frequency")
    
    
#     plt.hist(sec, bins=20, range=[min_n, 0.7], edgecolor="black", alpha=0.5, facecolor=colors[i-1], align="mid", label="01:0c:cd:01:00:0{0}".format(i))
    
#     # axs.hist(sec, bins=20, range=[min_n, 0.7], edgecolor="black", facecolor=colors[i-1], align="mid", label="01:0c:cd:01:00:0{0}".format(i))
#     # axs.set_title("01:0c:cd:01:00:0{0}".format(i))
#     # fig.savefig("test_hist_sec_{0}.png".format(i))

#     # print(df["01:0c:cd:01:00:0{0}".format(i)].describe())
#     # max = df["01:0c:cd:01:00:0{0}".format(i)].max()
#     # min = df["01:0c:cd:01:00:0{0}".format(i)].min()

#     # df.plot.hist(bins=10, column=["01:0c:cd:01:00:0{0}".format(i)], range=[min, max])
#     # plt.savefig("test_hist_sec_{0}.png".format(i))

# plt.legend(loc="upper right")
# now = datetime.now()
# axs.set_title("Without Security")
# # fig.savefig("test_hist_sec_{0}.png".format(i))
# fig.savefig(f"hist_no_sec_{now.strftime('%m_%d_%Y-%H_%M_%S')}.png")


if __name__ == '__main__':

    security = True
    # security = False
    
    main(security)