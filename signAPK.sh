#! /bin/sh

# zipalign=$ANDROID_HOME/build-tools/30.0.2/zipalign
zipalign -p 4 $1 $1.aligned

# zipalign doesn't work in place :(
mv $1.aligned $1


# apksigner=$ANDROID_HOME/build-tools/30.0.2/apksigner.bat
apksigner sign --ks "C:\Program Files\Java\jdk1.8.0_131\jre\bin\KeyStore.jks" --ks-key-alias "mydomain" --ks-pass pass:123456  $1

# remove generated signature file
rm $1.idsig

# jarsigner is outdated
# jarsigner -verbose -storepass 123456 -keystore "C:\Program Files\Java\jdk1.8.0_131\jre\bin\KeyStore.jks" $1 "mydomain"
