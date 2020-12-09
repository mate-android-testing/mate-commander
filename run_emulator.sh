#!/bin/bash

user_name=sellleon
read_user_name=sellleon

script_dir="/scratch/$user_name/home/mate-commander"
local_dir="/local/$user_name"
read_dir="/scratch/$read_user_name/home"
save_dir="/scratch/$user_name/save"

save_results () {
    echo "Saving log files"
    save_dir_ext=$save_dir/node-run_save_$(date --rfc-3339=seconds)_$(cat /proc/sys/kernel/random/uuid)_SLURM_ID_$SLURM_ARRAY_TASK_ID
    mkdir -p "$save_dir_ext"
    cp -r log "$save_dir_ext"
    cp *.png "$save_dir_ext"
    echo "Done"
}

cleanup_unmount() {
    echo "Umounting mountpoint: $TH"
    fusermount -zu $TH
    echo "Done."
}

cleanup_tmp_home () {
    echo "Removing temporary directory: $TH"
    rm -rf $TH
    echo "Done."
}

cleanup_tmp_dir_two () {
    echo "Removing temporary directory: $R"
    rm -rf $R
    echo "Done."
}

cleanup_tmp_dir () {
    echo "Removing temporary directory: $D"
    rm -rf $D
    echo "Done."
}

cleanup_proc_one() {
    echo "Cleaning up..."
    cleanup_tmp_dir
    echo "Cleanup done."
    echo "Bye."
    exit 1
}

cleanup_proc_two() {
    echo "Cleaning up..."
    cleanup_tmp_dir_two
    cleanup_tmp_dir
    echo "Cleanup done."
    echo "Bye."
    exit 1
}

cleanup_proc_three() {
    echo "Cleaning up..."
    cleanup_tmp_home
    cleanup_tmp_dir_two
    cleanup_tmp_dir
    echo "Cleanup done."
    echo "Bye."
    exit 1
}

cleanup_all() {
    echo "Cleaning up..."
    save_results
    cleanup_unmount
    cleanup_tmp_home
    cleanup_tmp_dir_two
    cleanup_tmp_dir
    echo "Cleanup done."
    echo "Bye."
}

cleanup_proc_four() {
    cleanup_all
    exit 1
}

echo "Creating path for tmp dir"
mkdir -p $local_dir
z=$?

if [[ $z == 0 ]]; then
    echo "Done."
else
    echo "Could not create path for tmp directories: $local_dir"
    exit 1
fi

echo "Creating tmp dir..."
D=`mktemp -d -p $local_dir`
r=$?

trap 'cleanup_proc_one;' INT TERM

if [[ $r == 0 ]]; then
    echo "Done."
else
    echo "Could not create temporary local directory in: $local_dir"
    exit 1
fi

echo "Creating second tmp dir..."
R=`mktemp -d -p $local_dir`
u=$?

trap 'cleanup_proc_two;' INT TERM

if [[ $u == 0 ]]; then
    echo "Done."
else
    echo "Could not create temporary local directory in: $local_dir"
    cleanup_proc_one
    exit 1
fi

echo "Creating temporary home dir..."
TH=`mktemp -d -p $local_dir`
q=$?

trap 'cleanup_proc_three;' INT TERM

if [[ $q == 0 ]]; then
    echo "Done."
else
    echo "Could not create temporary local directory in: $local_dir"
    cleanup_proc_two
    exit 1
fi

echo "Setting up environment..."
HOME=$TH
PATH="$HOME/Android/Sdk/platform-tools:$PATH"


echo "Mounting $read_dir RO with mountpoint $TH RW directory $D"
unionfs -o cow $D=RW:$read_dir=RO $TH
u_pid=$!
v=$?

trap 'cleanup_proc_four;' INT TERM

if [[ $v == 0 ]]; then
    echo "Done."
else
    echo "Mount failed"
    cleanup_proc_three
    exit 1
fi

echo "Changing to working directory $R"
cd $R

echo "Copying config files"
cp -r "$script_dir" .
cd "mate-commander"

echo "Copying images..."
device_id=$(grep device_id config.ini | awk '{print $3}')
mkdir -p $R/.android/
cp -r $read_dir/.android/avd $R/.android
echo path=$R/.android/avd/$device_id.avd >> $R/.android/avd/$device_id.ini

echo "Running commander"

ANDROID_EMULATOR_HOME=$HOME/.android ANDROID_AVD_HOME=$R/.android/avd ./commander.py --emulator_only &
pid=$!

wait $pid

echo "Commander done"

cleanup_all

exit 0
