#!/bin/bash

# You have to adjust the paths here!!!
MATE_HOME="C:\\Users\\Michael\\git\\mate"
MATE_SERVER_HOME="C:\\Users\\Michael\\git\\mate-server"
MATE_COMMANDER_HOME="C:\\Users\\Michael\\git\\mate-commander"

# build MATE APKs
cd $MATE_HOME
./gradlew assembleDebug
./gradlew assembleAndroidTest

# copy MATE APKs into mate-commander
cd $MATE_COMMANDER_HOME
cp $MATE_HOME\\app\\build\\outputs\\apk\\androidTest\\debug\\app-debug-androidTest.apk app-debug-androidTest.apk
cp $MATE_HOME\\app\\build\\outputs\\apk\\debug\\app-debug.apk app-debug.apk

# build MATE-Server jar
cd $MATE_SERVER_HOME
./gradlew fatJar

# copy MATE-Server jar into mate-commander
cd $MATE_COMMANDER_HOME
mkdir -p bin/
cp $MATE_SERVER_HOME\\build\\libs\\mate-server.jar bin\\mate-server.jar
