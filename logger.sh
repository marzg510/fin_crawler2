#!/bin/bash
OUT_STDOUT=0

function log() {
  local MSG=""
  if [ $# -lt 1 ]; then
    MSG=$(cat)
  else
    MSG=$(echo $@)
  fi
  local fname=${BASH_SOURCE[1]##*/}
  echo "${MSG}" | while read LINE; do
    LOGMSG="(${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) ${LINE}"
    logger ${LOGMSG}
    [[ $OUT_STDOUT -eq 1 ]] && echo "$(date +'%Y-%m-%d %T %Z') ${LOGMSG}"
  done
}
