#!/bin/bash

# $1 = emu_name
# $2 = app_id
# adb -s $1 root
adb -s $1 push "mediafiles/mateTestBmp.bmp" "sdcard/mateTestBmp.bmp"
adb -s $1 push "mediafiles/mateTestGif.gif" "sdcard/mateTestGif.gif"
adb -s $1 push "mediafiles/mateTestJpg.jpg" "sdcard/mateTestJpg.jpg"
adb -s $1 push "mediafiles/mateTestJson.json" "sdcard/mateTestJson.json"
adb -s $1 push "mediafiles/mateTestMid.mid" "sdcard/mateTestMid.mid"
adb -s $1 push "mediafiles/mateTestPdf.pdf" "sdcard/mateTestPdf.pdf"
adb -s $1 push "mediafiles/mateTestPng.png" "sdcard/mateTestPng.png"
adb -s $1 push "mediafiles/mateTestTiff.tiff" "sdcard/mateTestTiff.tiff"
adb -s $1 push "mediafiles/mateTestTxt.txt" "sdcard/mateTestTxt.txt"
adb -s $1 push "mediafiles/mateTestWav.wav" "sdcard/mateTestWav.wav"
adb -s $1 push "mediafiles/mateTestCsv.csv" "sdcard/mateTestCsv.csv"
adb -s $1 push "mediafiles/mateTestXml.xml" "sdcard/mateTestXml.xml"
adb -s $1 push "mediafiles/mateTestOgg.ogg" "sdcard/mateTestOgg.ogg"
adb -s $1 push "mediafiles/mateTestMp3.mp3" "sdcard/mateTestMp3.mp3"
