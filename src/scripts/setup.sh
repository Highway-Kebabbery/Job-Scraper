#!/data/data/com.termux/files/usr/bin/bash

# Test order:

# Post-restart
run: crontab -e    # Edit the crontab file to schedule tasks
Figure out how to programmatically add this to the editor and save results. 0 */3 * * * /data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/scripts/job_scraper.py    # YOU HAVE TO CREATE THIS BEFORE RUNNING SV-ENABLE CROND AND SV UP CROND
run: sv-enable crond    # Start the cronie service. Idk what this does # THIS NEEDS TO COME AFTER THE APP WAS EXITED FOLLOWING PKG INSTALL TERMUX-SERVICES
run: sv up crond    # Start the cronie service. Idk what this does
run: sv-enable atd    # ensure the atd daemon is running. Not sure what each of these does yet.
run: sv up atd    # ensure the atd daemon is running. Not sure what each of these does yet.

# Pre-restart
yes | pkg update -y
yes | pkg upgrade -y
termux-change-repo # Select Mirror group. On the next page, I selected North American mirrors. Use arrow keys, space, and enter to make selections.
yes | pkg install termux-api -y
yes | pkg install cronie -y    # For running the script periodically.
yes | pkg install at -y    # For scheduling the daily notification.
yes | pkg install python-pip -y
yes | pkg install x11-repo -y
yes | pkg install firefox -y
yes | pkg install geckodriver -y
pip install selenium==4.9.1 beautifulsoup4
chmod +x ../scrape_jobs.py ./schedule_scrape_jobs.sh    # Make the Python script executable
yes | pkg install termux-services -y # YOU HAVE TO FULLY EXIT THE APP AFTER INSTALLING TERMUX-SERVICES.




# Original order:
*yes | pkg update -y && yes | pkg upgrade -y
*termux-change-repo # Select Mirror group. On the next page, I selected North American mirrors. Use arrow keys, space, and enter to make selections.
*yes | pkg install python-pip -y
*pip install selenium==4.9.1 beautifulsoup4
*yes | pkg install x11-repo -y
*yes | pkg install firefox -y
*yes | pkg install geckodriver -y

*run: chmod +x <filepath to scrape_jobs.py> <filepath to shell script that sets/starts cron job>    # Make the Python script executable
*run: pkg install cronie    # For running the script periodically.
*run: pkg install at    # For scheduling daily notification
*run: yes | pkg install termux-services -y # YOU HAVE TO FULLY EXIT THE APP AFTER INSTALLING TERMUX-SERVICES. MAKE THIS THE LAST COMMAND BEFORE APP IS EXITED.

*run: crontab -e    # Edit the crontab file to schedule tasks
*Figure out how to programmatically add this to the editor and save results. 0 */3 * * * /data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/scripts/job_scraper.py    # YOU HAVE TO CREATE THIS BEFORE RUNNING SV-ENABLE CROND AND SV UP CROND
*run: sv-enable crond    # Start the cronie service. Idk what this does # THIS NEEDS TO COME AFTER THE APP WAS EXITED FOLLOWING PKG INSTALL TERMUX-SERVICES
*run: sv up crond    # Start the cronie service. Idk what this does
*run: sv-enable atd    # ensure the atd daemon is running. Not sure what each of these does yet.
*run: sv up atd    # ensure the atd daemon is running. Not sure what each of these does yet.

run: termux-setup-storage and grant permission. # Test to see if I can run commands after I run this. If I can, then run this right before pkg install termux-services, which requires a restart as well. termux-setup-storage isn't actually required in my application, but it's convenient to have set up. If I can't continue after running this, then take it out.
*run: pkg install termux-api



# Accompanying README.md instructions:

# Note: Force-quit the app if it begins entering "y" in an infinite loop. It's happened to me on very rare occasions.
# Select Mirror group. On the next page, I selected North American mirrors. Use arrow keys, space, and enter to make selections.