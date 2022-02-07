# Copy the toolchain's gdbserver to the Pi:
scp ~/opt/x-tools/aarch64-rpi3-linux-gnu/aarch64-rpi3-linux-gnu/debug-root/usr/bin/gdbserver RPi3:~
# Install it:
ssh RPi3 sudo mv gdbserver /usr/local/bin
# Test it:
ssh RPi3 gdbserver --version
# Start GDB with the hello program on your computer:
aarch64-rpi3-linux-gnu-gdb ~/RPi-dev/staging-aarch64-rpi3/bin/hello
# Inside of GDB, set the sysroot:
set sysroot /var/lib/schroot/chroots/rpi3-impish-arm64
# Select and start the target:
target remote | ssh RPi3 gdbserver - '~/.local/bin/hello' --name Pieter
# Run program:
continue
# Exit GDB:
quit