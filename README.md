# MATE-COMMANDER FOR LOCAL RUNS ON WINDOWS

The minimal requirements are:

* You need at least Java 11 and `JAVA_HOME` needs to exported to the `PATH`.
* You need a working `python3` installation.
* You need an Android SDK and an emulator, both come bundled with Android Studio.
* You need a bash on Windows, see https://gitforwindows.org/.
* The binary bash.exe needs to be on the `PATH`.
* The binary adb.exe needs to be on the `PATH`.
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
Now, run `buildMATE.sh <package-name>`. This will build and copy the relevant artifacts (apks, jar) into 
`MATE_COMMANDER_HOME`. Look at the notes below for obtaining the package name of the AUT.
NOTE: If your Java version is incompatible with the gradle version of MATE, you can use some older Java version by 
specifying `-Dorg.gradle.java.home="C:\\Program Files\\Java\\jdk-11"` when running the gradle commands.

The next step is to adjust the configuration file `config.ini` as follows:

* Specify the path of the emulator binary under the `[EMULATOR]` section, see the variable `command`.
* Specify the name of the AVD under the `[EMULATOR]` section, see the variable `device_id`. To create a new
AVD, open Android-Studio, click on the AVD-Manager and follow the instructions. Check the properties field for
the name of the AVD. We suggest to use either `Nexus 5` or `Pixel C` with API level 25/28/29. Note, however,
that you can't use a Google-PlayStore supported device like `Nexus 5` or `Nexus 5X` together with the suggested
Google-Play image due to permission issues; you have to fall back to one of the x86 images in this case.
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
`AndroidManifest.xml` file.

All other configurations of `MATE` and `MATE-Server` are controlled by adjusting the properties defined within
the files `mate.properties` and `mate-server.properties`, respectively. For instance, to control the timeout
you need to adjust the property `timeout` within the `mate.properties` file.

Optional steps:

* It is handy to have the `apktool` installed, see https://ibotpeaches.github.io/Apktool/. You can run
`apktool d <path-to-apk> -o <output-folder> -f` to decode an APK. Then, you can read for instance the package
name from the file `AndroidManifest.xml`, it's within the first few lines.
* It is also wise to have a keystore for signing APKs (right now `signAPK.sh` is using Android's default debugging keystore). 
  This step is mandatory whenever you modify an APK, e.g. instrument it with coverage information. Follow the steps at https://stackoverflow.com/questions/10930331/how-to-sign-an-already-compiled-apk.
Once you have a keystore, you need to adjust the file `signAPK.sh`. After that, you can sign an APK by supplying
the path of the APK as a command line argument.

Finally, you can invoke the `commander.py` as follows:
`python3 commander.py apps/<package-name>.apk`

NOTE: If you encounter permissions issues related to `python/python3`, prepend the command with `winpty`. If the output
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
Installing mate client...
Performing Streamed Install
Success

Done
Installing mate representation-layer...
Performing Streamed Install
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
Starting service: Intent { cmp=org.mate/.service.MATEService (has extras) }

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
cat log/emu.log | grep "MATE_SERVICE"
cat log/emu_err.log
cat log/server.log
cat log/server_err.log
```

Note that you have to clear the log folder after each run, otherwise the logs are appended
to the previous logs.

By default `commander.py` runs the emulator in headless mode. If you wish to see what
the emulator is actually doing, search for the flag `-no-window` within the file `commander.py`
and comment it out. If you like to debug the execution of `MATE`, add the flag `debug` to the
invocation of `commander.py`. Once the `MATE_SERVICE` log "MATE Service waiting for Debugger to 
be attached to Android Process" appears, you can attach your debugger through clicking
`Run -> Attach Debugger to Android Process -> org.mate` within Android Studio.


