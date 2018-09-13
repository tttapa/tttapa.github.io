#!/usr/bin/env bash
cd "$( dirname "${BASH_SOURCE[0]}" )"/../..
python3 -m http.server 8888 --bind 127.0.0.1