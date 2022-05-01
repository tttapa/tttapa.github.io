# See what toolchain files are available, use the one that matches your board.
ls cmake
# Configure the project using the correct toolchain.
cmake -S. -Bbuild \
    -DCMAKE_TOOLCHAIN_FILE="cmake/aarch64-rpi3-linux-gnu.cmake" \
    -DCMAKE_BUILD_TYPE=Debug
# Build the project.
cmake --build build -j
# Package the project.
pushd build; cpack; popd
# Copy the project to the Raspberry Pi.
ssh RPi3 tar xz < build/greeter-1.0.0-Linux-arm64.tar.gz
# Run the hello world program on the Pi.
ssh -t RPi3 greeter-1.0.0-Linux-arm64/bin/hello-world