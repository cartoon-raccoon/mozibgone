#!/usr/bin/bash

#! if you cloned the repository off github, this script will *not* work

function run_test() {
    shopt -s nullglob
    set +e

    mkdir test/{,/master}

    echo "[*] copying samples to test/master"
    cp samples/master/* test/master/

    array=(test/master/*)

    echo $array

    for exe in ${array[@]}; do
        output=$(printf "%s-unpacked" "$(printf "$(basename $exe)" | cut -b -8)")
        echo "doing $exe"
        if ./mozibgone.py -q -o "test/$output" "$exe"; then
            echo "$exe was successful"
        fi
        echo ""
    done
}

function reset() {
    rm -r test/
}

if [[ $1 == "-t" ]]; then
    echo "[*] running test"
    run_test
elif [[ $1 == "-r" ]]; then
    echo "[*] resetting"
    reset
else
    echo "?"
    exit 69 #nice
fi
