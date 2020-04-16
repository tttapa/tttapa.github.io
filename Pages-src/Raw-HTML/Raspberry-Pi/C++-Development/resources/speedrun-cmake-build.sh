cd build
ls ../cmake  # See what toolchain files are available
             # Use the one that matches your board
cmake .. \
    -DCMAKE_TOOLCHAIN_FILE=../cmake/aarch64-rpi3-linux-gnu.cmake \
    -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)