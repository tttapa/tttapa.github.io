# Copy the staging area archive to the Pi
# This command may take a while, depending on the speed of your SD card
scp ./toolchain/staging-aarch64-rpi3-linux-gnu.tar RPi3:/tmp
# Install everything to the root of the filesystem
# (will only install to /usr/local and /opt)
# Enter the sudo password of the Pi if necessary
# This command may take a while, depending on the speed of your SD card
ssh -t RPi3 "sudo tar xf /tmp/staging-aarch64-rpi3-linux-gnu.tar \
    -C / --strip-components=1 --keep-directory-symlink \
    --no-same-owner --no-same-permissions --no-overwrite-dir"
# Configure dynamic linker run-time bindings so newly installed libraries
# are found by the linker
# Enter the sudo password of the Pi if necessary
ssh -t RPi3 "sudo ldconfig"