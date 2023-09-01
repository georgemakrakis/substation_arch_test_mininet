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



def main (security):
    if security:
        prefix = "../1000/security_latencies_0"
        title = "With Security"
        now = datetime.now()
        final_name = f"box_sec_{now.strftime('%m_%d_%Y-%H_%M_%S')}.png"
        color = "lightblue"
    else:
        prefix = "../1000/learning_latencies_0"
        title = "Without Security"
        now = datetime.now()
        final_name = f"box_no_sec_{now.strftime('%m_%d_%Y-%H_%M_%S')}.png"
        color = "green"
    
    for i in range(1, 5):
        data = pd.read_csv("{0}{1}.csv".format(prefix,i))
        df = pd.DataFrame(data=data)
        print(df["01:0c:cd:01:00:0{0}".format(i)].max())
        sec = [i * 10000 for i in list(df.iloc[:, 1])]


        data_plt.append(sec)


    fig, ax = plt.subplots()
    plt.xlabel("Multicast Addresses", fontweight="bold")
    plt.ylabel("ms", fontweight="bold")
    plt.figure(figsize =(100, 100))
    #ax.boxplot(data_dict.values()) # With outliers
    ax.boxplot(data_plt,
            patch_artist = True,
            boxprops = dict(facecolor = color),
            showfliers=False)
    ax.set_xticklabels(multicast_addresses_scenario_1)
    # ax.set_xticks(len(multicast_addresses_scenario_1[0]*len(multicast_addresses_scenario_1)))

    # Creating plot
    # plt.boxplot(final_data)

    

    fig.savefig(final_name)


if __name__ == '__main__':

    security = True
    # security = False
    
    main(security)
