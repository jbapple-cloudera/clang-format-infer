CXX=/opt/Impala-Toolchain/gcc-4.9.2/bin/g++
CXXFLAGS=-W -Wall -Wextra -ggdb3 -O0 -std=c++11

CLANG_DIR=/opt/Impala-Toolchain/llvm-3.8.0-p1

search.exe: search.cc Makefile
	$(CXX) $(CXXFLAGS) -I$(CLANG_DIR)/include -o $@ $< -L$(CLANG_DIR)/lib \
	  $(shell cd ${CLANG_DIR}/lib && \
	  lorder *.a | tsort | sed 's/^lib/-l/g' | sed 's/\.a//g' \
	  | tr '\n' ']' | sed 's/\]/ /g') \
	  -lpthread -ldl
