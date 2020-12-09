#! /bin/sh

#BASE_DIR="~/git/mate-commander/"

package_name=$1

#APP_DIR="$BASE_DIR$package_name/"
APP_DIR="$package_name/"

echo "APP DIR: $APP_DIR"

# we need root access to push files onto the emulator
# adb root

# TODO: handle the case that ADB is not ready -> retry
# adb: error: failed to get feature set: no devices/emulators found

adb push "broadcast_actions.txt" "data/data/org.mate/"


