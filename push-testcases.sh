#! /bin/sh

#BASE_DIR="~/git/mate-commander/"

package_name=$1

#APP_DIR="$BASE_DIR$package_name/"
APP_DIR="apps/$package_name/"

TEST_CASE_DIR="test-cases"

INPUT_DIR="$APP_DIR$TEST_CASE_DIR"


echo "APP DIR: $APP_DIR"
echo "INPUT DIR: $INPUT_DIR"
echo "Pushing now Test Cases onto Emulator..."


# we need root access to push files onto the emulator
# adb root

adb shell mkdir data/data/org.mate/files

for file in $INPUT_DIR/*; do
    echo "$file"
    # adb push "$file" "data/data/org.mate/test-cases/"
    adb push "$file" "data/data/org.mate/files/"
done

