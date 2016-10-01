#!/bin/bash

OPTS=$(getopt -o '' --long cxx-compiler:,clang-format:,constants:,source-dir:,extensions:,repetitions: -- "$@")

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
        --repetitions)  REPETITIONS=$2;  shift 2;;
        *) break;;
    esac
done

REPETITIONS=${REPETITIONS:-"1"}

CLANG_DIR=$(dirname "${CLANG_FORMAT}")/..

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

make --directory="${THIS_DIR}" --silent CXX="${CXX_COMPILER}" CLANG_DIR="${CLANG_DIR}"

CXX_COMPILER_DIR=$(dirname "${CXX_COMPILER}")/..

EXAMPLE_STYLES=$(mktemp)

LD_LIBRARY_PATH="${CXX_COMPILER_DIR}"/lib64:${LD_LIBRARY_PATH} \
               "${THIS_DIR}/example-styles.exe" > "${EXAMPLE_STYLES}"

if [[ "${EXTENSIONS}" ]]
then
    OLD_SOURCE_DIR="${SOURCE_DIR}"
    NEW_SOURCE_DIR="$(mktemp -d)/$(basename ${OLD_SOURCE_DIR})"
    unset SOURCE_DIR

    cp -r "${OLD_SOURCE_DIR}" "${NEW_SOURCE_DIR}"
    find "${NEW_SOURCE_DIR}" -regextype posix-egrep -type f -not \
         -regex "^.*\.($EXTENSIONS)$" -execdir rm {} \;
    SOURCE_DIR="${NEW_SOURCE_DIR}"
fi

echo "Files: " $(find ${SOURCE_DIR} -type f | wc -l) >&2

BIG_CONFIG=$("${THIS_DIR}/search.py" --constants="${CONSTANTS}" \
                                     --clang-format="${CLANG_FORMAT}" \
                                     --source-dir="${SOURCE_DIR}" \
                                     --repetitions="${REPETITIONS}" < "${EXAMPLE_STYLES}")

cat "${EXAMPLE_STYLES}" | xargs -L 1 ${THIS_DIR}/re-style.sh \
    | "${THIS_DIR}/clang-format-reduce.py" --config "${BIG_CONFIG}" \
                                           --source-dir="${SOURCE_DIR}" \
                                           --clang-format="${CLANG_FORMAT}" \
                                           --constants="${CONSTANTS}"

rm "${BIG_CONFIG}"
xargs rm < "${EXAMPLE_STYLES}"
rm "${EXAMPLE_STYLES}"
