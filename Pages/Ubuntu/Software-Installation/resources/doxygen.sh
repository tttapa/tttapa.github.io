#!/usr/bin/env bash

set -ex

cd /tmp
git clone --branch Release_1_8_18 --depth 1 https://github.com/doxygen/doxygen.git
mkdir doxygen/build && cd doxygen/build
cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX=$HOME/.local ..
make -j`nproc`
make install