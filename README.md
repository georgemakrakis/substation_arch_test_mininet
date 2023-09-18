# substation_arch_test_mininet
Testing topologies and installation of flows, as a virtualized version of the substation network in CHE 203. It also accommodates IEC 61850 GOOSE communications evaluation for protection scenarios.


## Outline

The **experiments_wrapper.py** is used to initiate the experiments runs. It will create the Mininet environment described in **process_bus_mininet.py** and will launch the appropriate controller based on the option **security**. It also passed the parameter **scenario** that will perform the required message exchanged between the virtualized devices.

The two scenarios from above can be found in **goose_CHE_203_generic/** and **goose_CHE_203_generic_Scenario2/**. Since the complexity of Scenario 1 is less than that of Scenario 2, everything is combined in one file. For the second scenario, each device is a separate file, making it easy to change particular behavior and perform debugging if needed.

The PCAPs acquired from each experiment can be analyzed by **analysis/latency_analysis.py** and **analysis/latency_analysis_controller.py**. Once again, they include parameters for the secure and the non-secure version, as well as the scenario number.


