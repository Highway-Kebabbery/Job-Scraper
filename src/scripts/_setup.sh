#!/data/data/com.termux/files/usr/bin/bash

setup_mirrors() {
    local repo_file="$PREFIX/etc/apt/sources.list"
    echo "Setting up mirrors..."
    cat <<EOF > $repo_file
# North America mirrors
deb https://termux.mentality.rip/termux-main stable main
deb https://packages.termux.org/termux-main stable main
deb https://termux.mirror.server.com/termux-main stable main

# South American mirrors
deb https://termux.net.br mirror/termux stable main
deb https://termux.espelhosdigirati.com/termux stable main
deb https://termux.mirror.premi.st/termux stable main

# European mirrors
deb https://termux.mirror.eu/termux-main stable main
deb https://termux.mirror1.eu/termux-main stable main
deb https://termux.mirror2.eu/termux-main stable main
EOF
    echo "Mirrors set up successfully."
}

# Initial configuration
echo "Starting configuration..."
yes | pkg update -y
yes | pkg upgrade -y
setup_mirrors

echo "Installing dependencies..."
yes | pkg install termux-api -y
yes | pkg install cronie -y
yes | pkg install at -y
yes | pkg install python-pip -y
yes | pkg install x11-repo -y
yes | pkg install firefox -y
yes | pkg install geckodriver -y
pip install selenium==4.9.1
pip install beautifulsoup4
echo "dependencies installed"

# Remove .tar.gz file
rm -r Job-Scraper-*.tar.gz

# Make the Python and cronjob scheduling scripts executable.
chmod +x ./Job-Scraper-*/src/scrape_jobs.py
chmod +x ./Job-Scraper-*/src/scripts/_schedule_scrape_jobs.sh

run: termux-setup-storage and grant permission. # Technically optional. Gives Termux ability to see device storage folder.
yes | pkg install termux-services -y # YOU HAVE TO FULLY EXIT THE APP AFTER INSTALLING TERMUX-SERVICES.

echo -e "\n\n!!!!!!!\n"
echo -e "ATTENTION: Termux requires a full restart. Completely EXIT the app now.\n"
echo -e "!!!!!!!\n\n"
echo -e "Upon restart, execute ./<Job-Scraper-x.x>/src/scripts/_schedule_scrape_jobs.sh" to begin running the job scraper.
sleep 30

# Original order (verified functional):
#yes | pkg update -y && yes | pkg upgrade -y
#termux-change-repo # Select Mirror group. On the next page, I selected North American mirrors. Use arrow keys, space, and enter to make selections.
#yes | pkg install python-pip -y
#pip install selenium==4.9.1 beautifulsoup4
#yes | pkg install x11-repo -y
#yes | pkg install firefox -y
#yes | pkg install geckodriver -y

#run: chmod +x <filepath to scrape_jobs.py> <filepath to shell script that sets/starts cron job>    # Make the Python script executable
#run: pkg install cronie    # For running the script periodically.
#run: pkg install at    # For scheduling daily notification
#run: yes | pkg install termux-services -y # YOU HAVE TO FULLY EXIT THE APP AFTER INSTALLING TERMUX-SERVICES. MAKE THIS THE LAST COMMAND BEFORE APP IS EXITED.

#run: crontab -e    # Edit the crontab file to schedule tasks
#Figure out how to programmatically add this to the editor and save results. 0 #/3 * * * /data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/scripts/job_scraper.py    # YOU HAVE TO CREATE THIS BEFORE RUNNING SV-ENABLE CROND AND SV UP CROND
#run: sv-enable crond    # Start the cronie service. Idk what this does # THIS NEEDS TO COME AFTER THE APP WAS EXITED FOLLOWING PKG INSTALL TERMUX-SERVICES
#run: sv up crond    # Start the cronie service. Idk what this does
#run: sv-enable atd    # ensure the atd daemon is running. Not sure what each of these does yet.
#run: sv up atd    # ensure the atd daemon is running. Not sure what each of these does yet.

#run: termux-setup-storage and grant permission. # Test to see if I can run commands after I run this. If I can, then run this right before pkg install termux-services, which requires a restart as well. termux-setup-storage isn't actually required in my application, but it's convenient to have set up. If I can't continue after running this, then take it out.
#run: pkg install termux-api