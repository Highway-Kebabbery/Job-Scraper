#!/data/data/com.termux/files/usr/bin/bash

# Manually start termux-services. Restart still required after installing termux-services even if this command is run, but on occassion the restart wasn't enough to get termux-services up for me.
source $PREFIX/etc/profile.d/start-services.sh

# You need to set a cron job in the crontab before you try to run sv-enable crond or sv up crond
CRON_JOB="0 */3 * * * /data/data/com.termux/files/home/Job-Scraper-*/src/scrape_jobs.py"    # Run the scraper every three hours.
CRONJOB_FILE="/data/data/com.termux/files/home/crontab.tmp"

crontab -l > "$CRONJOB_FILE"

if ! grep -qF "$CRON_JOB" "$CRONJOB_FILE"; then
    echo "$CRON_JOB" >> "$CRONJOB_FILE"
fi

crontab "$CRONJOB_FILE"
rm "$CRONJOB_FILE"

sv-enable crond    # Start cronie service.
sv up crond    # Ensure cronie daemon is running.