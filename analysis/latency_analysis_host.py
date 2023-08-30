from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics


scenario_1_hosts = ["787_2_rec", "787_2_send", "451_2_rec", "451_2_send", "RTAC_rec", "RTAC_send", "651R_2_rec", "651R_2_send"]
scenario_1_dataframes = {"787_2_rec" : pd.DataFrame(), 
                         "787_2_send" : pd.DataFrame(), 
                         "451_2_rec" : pd.DataFrame(), 
                         "451_2_send" : pd.DataFrame(), 
                         "RTAC_rec" : pd.DataFrame(),
                         "RTAC_send" : pd.DataFrame(),
                         "651R_2_rec" : pd.DataFrame(), 
                         "651R_2_send" : pd.DataFrame(),
                        }

for index, device_name in enumerate(scenario_1_hosts):
    dir_path = "../goose_CHE_203_generic/logs_dir-{0}".format(device_name)
    for file_path in os.listdir(dir_path):
        # check if current file_path is a file
        if os.path.isfile(os.path.join(dir_path, file_path)):
            data = pd.read_csv("{0}/{1}".format(dir_path, file_path))
            scenario_1_dataframes[device_name] = pd.DataFrame(data=data)

# Analyze 651R_2 01:0C:CD:01:00:02

dev_RTAC_df = scenario_1_dataframes["RTAC_rec"]
dev_651R_2_df = scenario_1_dataframes["651R_2_send"]

print(dev_RTAC_df)
print(dev_651R_2_df)

# contain_values = dev_RTAC_df[dev_RTAC_df.iloc[:, 1].str.contains("SEL_651R_2/LLN0$GO$GooseDSet1")]
# print (contain_values)

