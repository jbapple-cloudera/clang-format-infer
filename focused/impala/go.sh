#!/bin/bash

IMPALA_CPP=$(mktemp -d)

cp -r "${IMPALA_HOME}/be/src/" "${IMPALA_CPP}"

rm -rf "${IMPALA_CPP}/gutil" "${IMPALA_CPP}/thirdparty"

echo "---"

../../clang-format-infer.sh \
    --cxx-compiler /opt/Impala-Toolchain/gcc-${IMPALA_GCC_VERSION}/bin/g++ \
    --clang-format /opt/Impala-Toolchain/llvm-${IMPALA_LLVM_VERSION}/bin/clang-format \
    --constants config-cpp \
    --source-dir "${IMPALA_CPP}" \
    --extensions='cc|h|c|cpp|cxx|hh|hpp'

echo "---"

../../clang-format-infer.sh \
    --cxx-compiler /opt/Impala-Toolchain/gcc-${IMPALA_GCC_VERSION}/bin/g++ \
    --clang-format /opt/Impala-Toolchain/llvm-${IMPALA_LLVM_VERSION}/bin/clang-format \
    --constants config-java \
    --source-dir "${IMPALA_HOME}/fe/src" \
    --extensions='java'
