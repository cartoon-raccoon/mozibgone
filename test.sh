#!/usr/bin/bash

#! if you cloned the repository off github, this script will *not* work
#! you will need a directory called test/master/ in your project root
#! that contains all your test samples

function run_test() {
    shopt -s nullglob

    if [[ -e test/ ]]; then
        echo "[!] test/ already exists, run ./test.sh -r first"
        exit 1
    fi

    mkdir test/{,/master}

    echo "[*] copying samples to test/master" >&2
    cp samples/master/* test/master/

    array=(test/master/*)

    declare -A results=(
        [total]=0
        [successes]=0
        [notupxpacked]=0
        [otherunpackerr]=0
        [nomoziheader]=0
        [parsingerror]=0
        [decodingerror]=0
    )

    echo $array

    for exe in ${array[@]}; do
        if [[ "$exe" == "test/master/fileinfo" ]]; then
            continue
        fi
        output=$(printf "%s-unpacked" "$(printf "$(basename $exe)" | cut -b -8)")
        echo "doing $exe"
        ((results[total]+=1))
        if ./mozibgone.py -q -o "test/$output" "$exe" >> test_result.txt; then
            ((results[successes]+=1))
            echo "$exe was successful" >&2
        else
            case $? in
            1)
                echo "?????"; exit 3
                ;;
            2)
                ((results[notupxpacked]+=1))
                ;;
            3)
                ((results[otherunpackerr]+=1))
                ;;
            4)
                ((results[nomoziheader]+=1))
                ;;
            5)
                ((results[parsingerror]+=1))
                ;;
            6)
                ((results[decodingerror]+=1))
                ;;
            *)
                echo "??????" exit 420
                ;;
            esac
        fi
        echo ""
    done

    echo "[*] final evaluation" >&2

    echo "total samples: ${results[total]}" >&2
    echo "successes: ${results[successes]}" >&2
    echo "failures:" >&2
    
    for i in "${!results[@]}"; do
        if [[ $i == "successes" ]] || [[ $i == "total" ]]; then
            continue
        fi

        failtype=$i
        failcount="${results[$i]}"
        if [[ $failcount != 0 ]]; then
            echo "  - $failtype : $failcount" >&2
        fi
    done
}

function reset() {
    rm -r test/
    rm test_result.txt
}

if [[ $1 == "-t" ]]; then
    echo "[*] running test" >&2
    run_test
elif [[ $1 == "-r" ]]; then
    echo "[*] resetting" >&2
    reset
else
    echo "?"
    exit 69 #nice
fi
