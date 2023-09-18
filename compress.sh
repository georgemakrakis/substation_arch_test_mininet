#!/bin/bash

#for i in {0..99}; do
for i in {0..199}; do
 #zip -ur "/home/mininet/substation_arch_test/scenario_2_exp/security_scenario_2_exp_200.zip" "/home/mininet/substation_arch_test/scenario_2_exp/security_scenario_2_exp_$i/"
 #zip -ur "/home/mininet/substation_arch_test/scenario_2_exp/learning_scenario_2_exp_200.zip" "/home/mininet/substation_arch_test/scenario_2_exp/learning_scenario_2_exp_$i/"

 #zip -ur "/home/mininet/substation_arch_test/scenario_1_exp/security_scenario_1_exp_200.zip" "/home/mininet/substation_arch_test/scenario_1_exp/security_scenario_1_exp_$i/"
 zip -ur "/home/mininet/substation_arch_test/scenario_1_exp/learning_scenario_1_exp_200.zip" "/home/mininet/substation_arch_test/scenario_1_exp/learning_scenario_1_exp_$i/"
done

