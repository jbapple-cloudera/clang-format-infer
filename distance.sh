#!/bin/bash

FORMATTER=$1
CONFIG=$2
DIR=$3

CELL=$(mktemp -d)

mkdir "${CELL}/new"

cp -r "${DIR}" "${CELL}/new"
cp "${CONFIG}" "${CELL}/.clang-format"

find "${CELL}/new" -type f -execdir "${FORMATTER}" -i -style=file {} \;

diff --suppress-common-lines -ru "${DIR}" "${CELL}/new/$(basename ${DIR})" | wc -l
