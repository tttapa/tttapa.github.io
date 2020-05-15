#!/usr/bin/env bash

# Script to download and install Eigen3

set -ex

version="3.3.7" # Release tag on GitLab
prefix="$HOME/.local"

cd /tmp
# Download
git clone --single-branch --depth=1 --branch "$version" \
    https://gitlab.com/libeigen/eigen.git
mkdir eigen/build && cd $_
# Configure
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$prefix"
# Install
make install