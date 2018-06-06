#!/usr/bin/env bash
if [ $# -ne 2 ]; then
    echo "Need provide two argument"
    exit 1
fi
python3 $(dirname "$0")/../tools/deploy/main.py $1 $2