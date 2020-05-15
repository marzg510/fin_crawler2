#!/bin/bash
. $(dirname $0)/logger.sh
#OUT_STDOUT=1
TARGET_DIR=${1:-.}

DAYS=60

log "sweep start target=${TARGET_DIR}"

for f in $(find ${TARGET_DIR} -mtime -${DAYS} -type f | sort); do
  for f2 in $(find ${TARGET_DIR} -cnewer $f -type f | sort); do
    [[ "$f" == "$f2" ]] && continue
    diff $f $f2 >/dev/null
    RET=$?
    if [ $RET -eq 0 ]; then
      log "detect dup : $(basename $f) == $(basename $f2) => rm $(basename $f)"
      rm -f $f
      break
    fi
  done
done

log "sweep end target=${TARGET_DIR}"

