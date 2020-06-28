#!/bin/bash

# sudo echo performance > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
sudo /home/pi/Desktop/ir/bin/remotecontroller.exe $1
# sudo echo ondemand > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor


## sudo sh -c "echo performance > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor"
## sudo /home/pi/Desktop/ir/bin/remotecontroller.exe $1
## sudo sh -c "echo ondemand > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor"
