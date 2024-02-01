# MATE-COMMANDER FOR LOCAL RUNS ON WINDOWS AND LINUX

The minimal requirements for Windows are:

* You need at least Java 11 and `JAVA_HOME` needs to exported to the `PATH`.
* You need a working `python3` installation.
* You need an Android SDK and an emulator, both come bundled with Android-Studio.
* You need a bash on Windows, see https://gitforwindows.org/.
* The binary bash.exe needs to be on the `PATH`.
* The binary adb.exe needs to be on the `PATH`.
* `ANDROID_HOME` need to be set and be on the `PATH`.
* A copy of MATE, see https://github.com/mate-android-testing/mate.
* A copy of MATE-Server, see https://github.com/mate-android-testing/mate-server.


The minimal requirements for Linux are:
* You need at least Java 11 and `JAVA_HOME` needs to exported to the `PATH`.
* You need a working `python3` installation.
* You need an Android SDK and an emulator, both come bundled with Android-Studio.
* The binary adb needs to be on the `PATH`.
* `ANDROID_HOME` need to be set and be on the `PATH`.
* A copy of MATE, see https://github.com/mate-android-testing/mate.
* A copy of MATE-Server, see https://github.com/mate-android-testing/mate-server.

Then, you need to adjust the paths within `buildMATE.sh`, e.g.:

```
MATE_HOME="C:\\Users\\Michael\\git\\mate"
MATE_SERVER_HOME="C:\\Users\\Michael\\git\\mate-server"
MATE_COMMANDER_HOME="C:\\Users\\Michael\\git\\mate-commander"
```

Create an empty `bin` folder within the mate-commander directory (this is where the MATE-Server jar will be placed).
Now, run `buildMATE.sh`. This will build and copy the relevant artifacts (apks, jar) into `MATE_COMMANDER_HOME`.
NOTE: On Windows, if your Java version is incompatible with the gradle version of MATE, you can use some older Java version by
specifying `-Dorg.gradle.java.home="C:\\Program Files\\Java\\jdk-11"` when running the gradle commands.

The next step is to adjust the configuration file `config.ini` as follows:

* Specify the path of the emulator binary under the `[EMULATOR]` section, see the variable `command`.
* Specify the name of the AVD under the `[EMULATOR]` section, see the variable `device_id`. To create a new
AVD, open Android-Studio, click on the AVD-Manager and follow the instructions. Check the properties field for
the name of the AVD. We suggest to use either `Nexus 5` or `Pixel C` with API level 25/28/29/30. Note, however,
that you can't use a Google-PlayStore supported device like `Nexus 5` or `Nexus 5X` together with the suggested
Google-Play image due to permission issues; you have to fall back to one of the x86 images or the Google API image in this case.
* Specify the test strategy under the `[MATE]` section, stick to `ExecuteMATERandomExploration` for initial testing.

The next steps are the following:

* Create an empty `log` folder within the mate-commander directory.
* Create an empty `apps` folder within the mate-commander directory.
* Put a sample APK into the aforementioned `apps` folder. The name must match the following convention:
`<package-name>.apk`. In order to derive the package name of an APK, you have two options. Either you use the
command `aapt dump badging <path-to-apk> | grep package:\ name` (aapt is shipped with the Android-SDK) or extract the
name from the `AndroidManifest.xml` using `apktool`. For initial testing we suggest the BMI-Calculator app from
https://f-droid.org/en/packages/com.zola.bmi/. The package name for this app is: **com.zola.bmi**, hence rename the APK
to com.zola.bmi.apk.
* Create an additional folder also matching the package name within the `apps` folder. For the BMI-Calculator app
this means a folder named `com.zola.bmi`. This is the place where you put additional resources for certain testing
strategies or where `MATE` writes coverage information for instance. Right now, this app specific folder needs to contain
at least the `AndroidManifest.xml`. Thus, the simplest option is to call `apktool d <packagename>.apk` within the `apps`
folder and this will produce the required folder, e.g. `com.zola.bmi` for the BMI-Calculator app, containing the
`AndroidManifest.xml` file. In addition, you need to place a folder called `static_data` that you obtain from running the
  `dexanalyzer` tool (https://github.com/mate-android-testing/dexanalyzer) inside the app folder. Ideally, you want to
  measure coverage by using the `WallMauer` tool (https://github.com/mate-android-testing/wallmauer). In this case you
  need to place the obtained artefacts into the app folder as well, see 
  https://github.com/mate-android-testing/wallmauer?tab=readme-ov-file#mate-integration.
* Adjust the script `signAPK.sh` that is responsible for signing the APKs. In particular, you have to define the paths
to the two binaries `apksigner` and `zipalign` that come bundled with the Android SDK. If you wish to use your own keystore
  follow the instructions at: https://stackoverflow.com/questions/10930331/how-to-sign-an-already-compiled-apk.

All other configurations of `MATE` and `MATE-Server` are controlled by adjusting the properties defined within
the files `mate.properties` and `mate-server.properties`, respectively. For instance, to control the timeout
you need to adjust the property `timeout` within the `mate.properties` file.

Optional steps:

* It is handy to have the `apktool` installed, see https://ibotpeaches.github.io/Apktool/. You can run
`apktool d <path-to-apk> -o <output-folder> -f` to decode an APK. Then, you can read for instance the package
name from the file `AndroidManifest.xml`, it's within the first few lines.

Finally, you can invoke the `commander.py` as follows:
`python3 commander.py apps/<package-name>.apk`

In case you want to **debug** `MATE`, invoke the `commander.py` with an additional argument `debug`. Once the log
_"Waiting for debugger!"_ appears in the output of `adb logcat`, attach the debugger inside Android Studio as follows:
`Run -> 'Attach Debugger to Android Process' -> 'org.mate'`

NOTE: On Windows, if you encounter permissions issues related to `python/python3`, prepend the command with `winpty`. If the output
shows a 'adb not found' log, then ensure that `adb` is really on the `PATH` and/or append the flag `shell=True` to the
respective `subprocess.run()` invocation within `commander.py`!

This should produce an output similar to the following:

```
$ ./commander.py apps/com.zola.bmi.apk
Using Emulator
Emulator logging enabled. Logging to log/emu.log and log/emu_err.log
Starting Emulator...
Emulator invoked!
Done emulator init!
Emulator: emulator-5554
Emulator online!
Flags:
Installing app: com.zola.bmi.apk...
Performing Streamed Install
Success

Done
Pushing mate...
app-debug.apk: 1 file pushed, 0 skipped. 776.7 MB/s (3947580 bytes in 0.005s)

Done
Installing mate...
Success

Done
Pushing mate tests...
app-debug-androidTest.apk: 1 file pushed, 0 skipped. 579.2 MB/s (1871063 bytes in 0.003s)

Done
Installing mate tests...
Success

Done
Creating files dir
Done.
Server logging enabled. Logging to log/server.log and log/server_err.log
Starting mate server...
Starting app...
Events injected: 1
## Network stats: elapsed time=15ms (0ms mobile, 0ms wifi, 15ms not connected)

Done
Restarting ADB as root...
bash.exe --login -i -c 'adb -s emulator-5554 root'


Done
Wait for app to finish starting up...
Running tests...
INSTRUMENTATION_STATUS: numtests=1
INSTRUMENTATION_STATUS: stream=
org.mate.ExecuteMATERandomExploration:
INSTRUMENTATION_STATUS: id=AndroidJUnitRunner
INSTRUMENTATION_STATUS: test=useAppContext
INSTRUMENTATION_STATUS: class=org.mate.ExecuteMATERandomExploration
INSTRUMENTATION_STATUS: current=1
INSTRUMENTATION_STATUS_CODE: 1
INSTRUMENTATION_STATUS: numtests=1
INSTRUMENTATION_STATUS: stream=.
INSTRUMENTATION_STATUS: id=AndroidJUnitRunner
INSTRUMENTATION_STATUS: test=useAppContext
INSTRUMENTATION_STATUS: class=org.mate.ExecuteMATERandomExploration
INSTRUMENTATION_STATUS: current=1
INSTRUMENTATION_STATUS_CODE: 0
INSTRUMENTATION_RESULT: stream=

Time: 217.188

OK (1 test)


INSTRUMENTATION_CODE: -1

Done
Closing emulator...
bash.exe --login -i -c 'adb -s emulator-5554 emu kill'
OK: killing emulator, bye bye
OK

Done
```

The displayed time should match roughly the specified timeout (+ ~30 seconds for clean up).
If there is any error, you can check the logs produced by `MATE` and `MATE-Server`, e.g. check:

```
cat log/emu.log | grep "E acc"
cat log/emu.log | grep "apptest"
cat log/emu_err.log
cat log/server.log
cat log/server_err.log
```

Note that you have to clear the log folder after each run, otherwise the logs are appended
to the previous logs.

By default `commander.py` runs the emulator in the foreground. If you want to run the emulator in headless mode,
append the flag `-no-window` to the emulator start options. On Linux, you may want to enable the flag `-enable-kvm` as well.

## Scripts

You can use below script to generate the required artefacts by MATE for multiple apps. The script is invoked by providing
as first argument the folder containing the plain APKs and as second argument the folder where the instrumented APKs
and the app folders should be placed. You would typically invoke the script via `nohup` since this can be a long-running
task depending on the number of apps to instrument as follows:

```
nohup bash instrumentBasicBlockCoverage.sh test_dir/plain-apps test_dir/apps >> instrumentation.log & 
```

The required binaries, i.e., `basicBlockCoverage.jar` and `dexanalyzer.jar`, can be built from the respective repositories
https://github.com/mate-android-testing/wallmauer and https://github.com/mate-android-testing/dexanalyzer.
You may require a different instrumentation binary depending on the type of coverage/fitness you intend to measure
and consequently need to adjust the binary name accordingly in below script.

```
#!/bin/bash

# contains the plains APKs
INPUT=$1

# will contain the instrumented APKs + for each app a directory containing the mandatory artefacts
OUTPUT=$2

# track how many apps could be sucessfully instrumented
success=0

for file in $INPUT/*.apk; do

    # rename the APK
    packageName=$(aapt dump badging $file | awk -v FS="'" '/package: name=/{print $2}')
    echo "Package name: $packageName"

    orig_file=$file

    # only rename if necessary
    if [[ $file != "$INPUT/$packageName.apk" ]]
    then
        cp $file "$INPUT/$packageName.apk"
        file="$INPUT/$packageName.apk"
    fi

    # file name without .apk extension and path
    base=$(basename $file)
    base=${base%.apk}

    # skip if (instrumented) APK already exists in output folder, use -f to overwrite
    if [[ -f "$OUTPUT/$base.apk" ]] && [[ $3 != "-f" ]]
    then
        echo "Skipping $file"
        if [[ $file != $orig_file ]]
        then
            rm $file
        fi
        continue
    fi

    # remove a previous blocks.txt
    rm -f blocks.txt
    rm -f branches.txt
    # rm -f instrumentation-points.txt (only required in combination with branchDistance.jar binary)

    echo "Instrumenting app $base ..."
    java -Djdk.util.zip.disableZip64ExtraFieldValidation=true -Djdk.nio.zipfs.allowDotZipEntry=true -jar basicBlockCoverage.jar "$file" "--only-aut"

    if ! [[ -f "$INPUT/$base-instrumented.apk" ]]
    then
        echo "Couldn't instrument app $base!"
        continue
    fi

    # no blocks.txt typically exists if no core application class could be instrumented
    if ! [[ -f blocks.txt ]]
    then
        echo "No blocks.txt for app $base!"
        # remove the instrumented apk
        rm -f "$INPUT/$base-instrumented.apk"
        continue
    fi

    # output file name
    instrumented="$INPUT/$base-instrumented.apk"
    mv $instrumented "$OUTPUT/$base.apk"

    instrumented="$OUTPUT/$base.apk"

    echo "Signing app $base ..."
    bash signAPK.sh $instrumented

    echo "apktool d $base -f ..."
    apktool d $instrumented -s -o "$OUTPUT/$base" -f

    echo "Generating static intent info ..."
    java -Djdk.util.zip.disableZip64ExtraFieldValidation=true -Djdk.nio.zipfs.allowDotZipEntry=true -jar dexanalyzer.jar $file
    mkdir -p $OUTPUT/$base/static_data
    mv $INPUT/$base/static_data/* $OUTPUT/$base/static_data/
    rm -rf "$INPUT/$base"

    # if we renamed the file (copied), we should delete the copy
    if [[ $file != $orig_file ]]; then
         rm $file
    fi

    echo "Move blocks.txt to app directory ..."
    mv blocks.txt "$OUTPUT/$base/"
    mv branches.txt "$OUTPUT/$base/"
    # mv instrumentation-points.txt "$OUTPUT/$base/" (only required in combination with branchDistance.jar binary)

    success=$((success+1))

done

echo "Could successfully instrument $success apps!"
```
