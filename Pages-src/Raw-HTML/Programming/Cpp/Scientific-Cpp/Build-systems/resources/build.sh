mkdir -p build
g++ -std=c++20 -c liba/a.cpp -I liba -o build/a.o            # ╮
g++ -std=c++20 -c libb/b.cpp -I liba -I libb -o build/b.o    # ├ ➊
g++ -std=c++20 -c main.cpp -I libb -o build/main.o           # ╯
g++ build/{a,b,main}.o -lfmt -o build/main                   # ─ ➋
./build/main