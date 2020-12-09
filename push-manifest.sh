#! /bin/sh

#BASE_DIR="~/git/mate-commander/"

package_name=$1

#APP_DIR="$BASE_DIR$package_name/"
APP_DIR="apps/$package_name/"

echo "APP DIR: $APP_DIR"

# we need root access to push files onto the emulator
# adb root

adb push "${APP_DIR}AndroidManifest.xml" "data/data/org.mate/"


