.phony: default all clean test

default: all

ldpc: ldpc.cu
	nvcc --compiler-bindir /usr/bin/g++-12 $< -o $@

test: ldpc
	./ldpc

all: ldpc

clean:
	-rm -f ldpc
