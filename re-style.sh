#!/bin/bash

RESULT=$(mktemp)

sed 's/^# BasedOnStyle/BasedOnStyle/' "$1" >"${RESULT}"

echo "${RESULT}"
