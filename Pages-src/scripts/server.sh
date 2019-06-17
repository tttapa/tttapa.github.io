#!/usr/bin/env bash
cd "$( dirname "${BASH_SOURCE[0]}" )"/../..
if [ "$1" == "public" ]
then
    python3 -m http.server 8888 --bind 0.0.0.0
else
    python3 -m http.server 8888 --bind 127.0.0.1
fi