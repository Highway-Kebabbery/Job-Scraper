#!/data/data/com.termux/files/usr/bin/bash

# Manually start termux-services. Restart still required after installing termux-services even if this command is run, but on occassion the restart wasn't enough to get termux-services up for me.
source $PREFIX/etc/profile.d/start-services.sh

# You need to set a cron job in the crontab before you try to run sv-enable crond or sv up crond
CRONJOB_FILE="/data/data/com.termux/files/home/crontab.tmp"

SCRAPE_CRON_JOB="0 */3 * * * python /data/data/com.termux/files/home/Job-Scraper-*/src/scrape_jobs.py"    # Run the scraper every three hours.
DAILY_CRON_JOB="0 10 * * * python /data/data/com.termux/files/home/Job-Scraper-*/src/scripts/_daily_notif_handler.py"    # Run the daily notification handler daily at 1000 local time

crontab -l > "$CRONJOB_FILE" 2>/dev/null || true

for job in "$SCRAPE_CRON_JOB" "$DAILY_CRON_JOB"; do
    if ! grep -qxF "$job" "$CRONJOB_FILE"; then
        echo "$job" >> "$CRONJOB_FILE"
    fi
done

crontab "$CRONJOB_FILE"
rm "$CRONJOB_FILE"

sv-enable crond    # Start cronie service.
sv up crond    # Ensure cronie daemon is running.