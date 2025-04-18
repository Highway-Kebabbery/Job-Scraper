#!/data/data/com.termux/files/usr/bin/bash

SCRIPTDIR="/data/data/com.termux/files/home/Job-Scraper-*/src/scripts/daily-scripts"

# All shell scripts
for notif in "$SCRIPTDIR"/*.sh; do
  [ -x "$notif" ] || continue
  "$notif"
  rm "$notif"
done