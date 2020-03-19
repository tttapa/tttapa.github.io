cd build
ls ../cmake/*Toolchain*  # See what toolchain files are available
                         # Use the one that matches your board
cmake .. \
    -DCMAKE_TOOLCHAIN_FILE=../cmake/RPi3-Toolchain-AArch64.cmake \
    -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)