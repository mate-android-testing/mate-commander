# MATE-COMMANDER FOR LOCAL RUNS ON WINDOWS

The minimal requirements are:

You need a bash on Windows -> https://gitforwindows.org/
bash.exe needs to be on the PATH
adb.exe needs to be on the PATH
ANDROID_HOME need to be set and be on the PATH

Before you can start commander.py, you have to perform the following steps:

Create an empty 'log' folder in this directory.
Create an 'apps' folder.
Put a sample app (the APK) into the 'apps' folder. You may try out the simple BMI-Calculator app from https://f-droid.org/en/packages/com.zola.bmi/.
The name of the APK file must follow the convention: <package-name>.apk (e.g. com.zola.bmi.apk)
Create an corresponding 'app' folder within the 'apps' folder. The same rule as above applies, e.g. com.zola.bmi

To invoke the commander, type:

python3 commander.py apps/<package-name>.apk 




