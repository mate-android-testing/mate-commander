#!/bin/bash

# we need to re-build the MATE APKs for each target app separately
packageName=$1

# You have to adjust the paths here!!!
MATE_HOME="C:\\Users\\Michael\\git\\mate"
MATE_SERVER_HOME="C:\\Users\\Michael\\git\\mate-server"
MATE_COMMANDER_HOME="C:\\Users\\Michael\\git\\mate-commander"

# Print message and exit
die() { echo "$*" 1>&2 ; exit 1; }

# Check if $ANDORID_HOME is set
[[ -n ${ANDROID_HOME+x} ]] || die "ANDROID_HOME is not set"

# Check if adb is in $PATH
type -P 'adb' > /dev/null || die "adb is not in path"

# Check fi MATE_HOME, MATE_SERVER_HOME and MATE_COMMANDER_HOME refer to
# directories.
[[ -d "$MATE_HOME" ]] || die "MATE_HOME does not point to a directory"
[[ -d "$MATE_SERVER_HOME" ]] || die "MATE_SERVER_HOME does not point to a directory"
[[ -d "$MATE_COMMANDER_HOME" ]] || die "MATE_COMMANDER_HOME does not point to a directory"


# build MATE APKs
cd $MATE_HOME

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # kill idle gradle tasks
    status=$(./gradlew --status)

    # split on new line
    IFS=$'\n'; set -f; lines=($status)

    # kill idle gradle tasks
    for line in "${lines[@]}"
    do
        if [[ $line =~ "IDLE" ]]
        then
            pid=$(echo $line | grep -o -E '[0-9]+' | head -1 | sed -e 's/^0\+//')
            kill -9 $pid
        fi
    done
fi


# if Java 15 is not working, use Java 11, e.g. ./gradlew -Dorg.gradle.java.home="C:\\Program Files\\Java\\jdk-11" assembleDebug
./gradlew :representation:clean :representation:assembleDebugAndroidTest -PtargetPackage=$packageName
./gradlew :client:clean :client:assembleDebug

# copy MATE APKs into mate-commander
cd $MATE_COMMANDER_HOME

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cp $MATE_HOME/representation/build/outputs/apk/androidTest/debug/representation-debug-androidTest.apk representation-debug-androidTest.apk
    cp $MATE_HOME/client/build/outputs/apk/debug/client-debug.apk client-debug.apk
elif [[ "$OSTYPE" == "msys" ]]; then
    cp $MATE_HOME\\representation\\build\\outputs\\apk\\androidTest\\debug\\representation-debug-androidTest.apk representation-debug-androidTest.apk
    cp $MATE_HOME\\client\\build\\outputs\\apk\\debug\\client-debug.apk client-debug.apk
else
    die "Cannot build Mate: Unknown operating system"
fi

# sign the APKs with the same key as the APK of the AUT
./signAPK.sh representation-debug-androidTest.apk
./signAPK.sh client-debug.apk

# build MATE-Server jar
cd $MATE_SERVER_HOME
./gradlew fatJar

# copy MATE-Server jar into mate-commander
cd $MATE_COMMANDER_HOME
mkdir -p bin/

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cp $MATE_SERVER_HOME/build/libs/mate-server.jar bin/mate-server.jar
elif [[ "$OSTYPE" == "msys" ]]; then
    cp $MATE_SERVER_HOME\\build\\libs\\mate-server.jar bin\\mate-server.jar
else
    die "Cannot build Mate Server: Unknown operating system"
fi
