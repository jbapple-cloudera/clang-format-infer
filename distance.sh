#!/bin/bash

FORMATTER=$1
CONFIG=$2
DIR=$3

CELL=$(mktemp -d)

mkdir "${CELL}/new"

cp -r "${DIR}" "${CELL}/new"
cp "${CONFIG}" "${CELL}/.clang-format"

find "${CELL}/new" -type f -print0 | xargs -0 -n 1 -P 0 "${FORMATTER}" -i -style=file

diff --suppress-common-lines -ru "${DIR}" "${CELL}/new/$(basename ${DIR})" | wc -l

rm -rf "${CELL}"
