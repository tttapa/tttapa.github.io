#!/usr/bin/env bash
cd "$( dirname "${BASH_SOURCE[0]}" )"/../..
port=${2:-8889}
if [ "$1" == "public" ]
then
    python3 -m http.server $port --bind 0.0.0.0
else
    python3 -m http.server $port --bind 127.0.0.1
fi