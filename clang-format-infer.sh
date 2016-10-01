#!/bin/bash

OPTS=$(getopt -o '' --long cxx-compiler:,clang-format:,constants:,source-dir:,extensions: -- "$@")

eval set -- "$OPTS"

CXX_COMPILER=$(whereis clang++ | cut -d ' ' -f 2)
CLANG_FORMAT=$(whereis clang-format | cut -d ' ' -f 2)

while true; do
    case "$1" in
        --cxx-compiler) CXX_COMPILER=$2; shift 2;;
        --clang-format) CLANG_FORMAT=$2; shift 2;;
        --constants)    CONSTANTS=$2;    shift 2;;
        --source-dir)   SOURCE_DIR=$2;   shift 2;;
        --extensions)   EXTENSIONS=$2;   shift 2;;
        *) break;;
    esac
done

CLANG_DIR=$(dirname "${CLANG_FORMAT}")/..

make CXX="${CXX_COMPILER}" CLANG_DIR="${CLANG_DIR}"

CXX_COMPILER_DIR=$(dirname "${CXX_COMPILER}")/..

LD_LIBRARY_PATH="${CXX_COMPILER_DIR}"/lib64:${LD_LIBRARY_PATH} ./example-styles.exe \
    | ./search.py --constants="${CONSTANTS}" --clang-format="${CLANG_FORMAT}" \
                  --source-dir="${SOURCE_DIR}"
