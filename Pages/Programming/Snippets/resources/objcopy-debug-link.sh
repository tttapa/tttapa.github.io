# Dependencies and dynamic section of a shared library
objcopy -O binary --dump-section .gnu_debuglink=>(cut -d '' -f 1 -) libfile.so