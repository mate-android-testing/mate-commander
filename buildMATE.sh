#!/bin/bash

# we need to re-build the MATE APKs for each target app separately
packageName=$1

# You have to adjust the paths here!!!
MATE_HOME="C:\\Users\\Michael\\git\\mate"
MATE_SERVER_HOME="C:\\Users\\Michael\\git\\mate-server"
MATE_COMMANDER_HOME="C:\\Users\\Michael\\git\\mate-commander"

# build MATE APKs
cd $MATE_HOME
# if Java 15 is not working, use Java 11, e.g. ./gradlew -Dorg.gradle.java.home="C:\\Program Files\\Java\\jdk-11" assembleDebug
./gradlew :representation:clean :representation:assembleDebugAndroidTest -PtargetPackage=$packageName
./gradlew :client:clean :client:assembleDebug

# copy MATE APKs into mate-commander
cd $MATE_COMMANDER_HOME
cp $MATE_HOME\\representation\\build\\outputs\\apk\\androidTest\\debug\\representation-debug-androidTest.apk representation-debug-androidTest.apk
cp $MATE_HOME\\client\\build\\outputs\\apk\\debug\\client-debug.apk client-debug.apk

# sign the APKs with the same key as the APK of the AUT
./signAPK.sh representation-debug-androidTest.apk
./signAPK.sh client-debug.apk

# sign the APKs with the same key as the APK of the AUT
./signAPK.sh app-debug-androidTest.apk
./signAPK.sh app-debug.apk

# build MATE-Server jar
cd $MATE_SERVER_HOME
./gradlew fatJar

# copy MATE-Server jar into mate-commander
cd $MATE_COMMANDER_HOME
mkdir -p bin/
cp $MATE_SERVER_HOME\\build\\libs\\mate-server.jar bin\\mate-server.jar
