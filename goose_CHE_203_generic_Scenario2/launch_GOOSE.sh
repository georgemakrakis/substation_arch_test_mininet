#!/bin/bash
# xterm -e bash -c "make && sudo ./goose_CHE_203_generic_Scenario2 lo 651R_2"
# xterm -e bash -c "make && sudo ./goose_CHE_203_generic_Scenario2 lo 451_2"
# xterm -e bash -c "make && sudo ./goose_CHE_203_generic_Scenario2 lo 487B_2"
# xterm -e bash -c "make && sudo ./goose_CHE_203_generic_Scenario2 lo 351_2"

make
sudo ./goose_CHE_203_generic_Scenario2 lo 651R_2 & sudo ./goose_CHE_203_generic_Scenario2 lo 451_2 & \
sudo ./goose_CHE_203_generic_Scenario2 lo 487B_2 & sudo ./goose_CHE_203_generic_Scenario2 lo 351_2 \
&& fg