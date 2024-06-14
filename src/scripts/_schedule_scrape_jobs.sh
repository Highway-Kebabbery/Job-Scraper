#!/data/data/com.termux/files/usr/bin/bash

# This script checks to see if the Job scraper's cronjob exists in the crontab and, if not, adds it.

# As a note to self: You need to set a cron job in the crontab before you try to run sv-enable crond or sv up crond
CRON_JOB="0 */3 * * * /data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/scripts/job_scraper.py"    # Run the scraper every three hours.
CRONJOB_FILE="/data/data/com.termux/files/home/crontab.tmp"

touch "$CRONJOB_FILE"

if ! grep -qF "$CRON_JOB" "$CRONJOB_FILE"; then
    echo "$CRON_JOB" >> "$CRONJOB_FILE"
fi

crontab "$CRONJOB_FILE"
rm "$CRONJOB_FILE"

sv-enable crond    # Start cronie service.
sv up crond    # Ensure cronie daemon is running.