#!/bin/bash

package_name=$1
emu_name=$2

# try restarting adb as root
response=$(adb -s $2 root 2>&1)
echo "Response: $response"

if [[ $response == *"adb: error: failed to get feature set: device offline"* || $response == *"adb: unable to connect for root: device offline"* ]]; then
    echo "ADB connection corrupted! Try-reconnecting..."
    adb devices
    sleep 20
    adb devices
    adb kill-server
    adb start-server
    adb devices
    adb -s $2 root
fi
