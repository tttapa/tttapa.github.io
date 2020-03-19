# Run the tests
ssh -t RPi3 "/tmp/greeter.test"

# Run the Hello World program
ssh -t RPi3 "/tmp/hello-world"

# Alternatively, start an interactive SSH session, and run it on the Pi directly
ssh RPi3