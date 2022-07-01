#!/bin/bash

# adjust the path accordingly!
zipalign=$ANDROID_HOME/build-tools/31.0.0/zipalign
apksigner=$ANDROID_HOME/build-tools/31.0.0/apksigner

$zipalign -p 4 $1 $1.aligned

# There is a bug with zipalign, we need two iterations.
# See: https://stackoverflow.com/questions/38047358/zipalign-verification-failed-resources-arsc-bad-1
$zipalign -f -p 4 $1.aligned $1.aligned2

rm $1.aligned
mv $1.aligned2 $1

$apksigner sign --ks ~/.android/debug.keystore --ks-key-alias androiddebugkey --ks-pass pass:android --key-pass pass:android $1

# alternatively create your own keystore: https://stackoverflow.com/questions/3997748/how-can-i-create-a-keystore
# apksigner sign --ks "C:\Program Files\Java\jdk1.8.0_131\jre\bin\KeyStore.jks" --ks-key-alias "mydomain" --ks-pass pass:123456  $1

# remove generated signature file
rm $1.idsig
