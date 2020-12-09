#!/bin/bash
# You have to adjust the paths here!!!
cd ~/git/mate/

./gradlew assembleDebug
./gradlew assembleAndroidTest

cd ~/git/mate-commander/

cp C:\\Users\\Michael\\git\\mate\\app\\build\\outputs\\apk\\androidTest\\debug\\app-debug-androidTest.apk app-debug-androidTest.apk
cp C:\\Users\\Michael\\git\\mate\\app\\build\\outputs\\apk\\debug\\app-debug.apk app-debug.apk

cd ~/git/mate-server/
./gradlew fatJar

cd ~/git/mate-commander/

cp C:\\Users\\Michael\\git\\mate-server\\build\\libs\\mate-server.jar bin\\mate-server.jar
