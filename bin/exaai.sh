#!/usr/bin/env bash
if [ $# -ne 1 ]; then
    echo "Need provide one argument"
    exit 1
fi
python3 $(dirname "$0")/../tools/exaai/exaai.py $1