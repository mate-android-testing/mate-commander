#!/bin/bash

package_name=$1
APP_DIR="apps/$package_name/"
echo "APP DIR: $APP_DIR"
adb push "${APP_DIR}static_data/staticStrings.xml" "data/data/org.mate/staticStrings.xml"


