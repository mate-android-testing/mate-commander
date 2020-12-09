#! /bin/sh

package_name=$1

APP_DIR="apps/$package_name/"
OUTPUT_DIR="$APP_DIR"

echo "Saving test cases into: $OUTPUT"
mkdir -p $OUTPUT_DIR

echo "TestCases present on emulator: "
adb shell ls data/data/org.mate/test-cases/

echo "Retrieving now Test Cases from Emulator..."
adb pull data/data/org.mate/test-cases/ "$OUTPUT_DIR"




