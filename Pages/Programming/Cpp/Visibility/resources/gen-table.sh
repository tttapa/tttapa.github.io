#!/usr/bin/env bash

set -euxo pipefail

cd "$(dirname "$0")"
export CC=gcc-11
export CXX=gcc-11
cmake --fresh -B build -G 'Unix Makefiles'
cmake --build build --clean-first > readelf.txt
python3 parse_readelf.py
echo "Ok"
