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

# This uh... won't work if they download more than one version of the project. Oops.
# OIIIIIII. I'm going to try setting 755 permissions for the entire project folder instead of just _setup.sh in the beginning. These may be obselete after that.
#chmod 755 ./Job-Scraper-*/src/scrape_jobs.py
#chmod 755 ./Job-Scraper-*/src/scripts/_schedule_scrape_jobs.sh

termux-setup-storage    # Technically optional. Gives Termux ability to see device storage folder. Need to exit to complete setup.
yes | pkg install termux-services -y    # YOU HAVE TO FULLY EXIT THE APP AFTER INSTALLING TERMUX-SERVICES.

echo -e "\n\n!!!!!!!\n"
echo -e "ATTENTION: Termux requires a full restart. Completely EXIT the app now.\n"
echo -e "!!!!!!!\n\n"
echo -e "Upon restart, execute ./<Job-Scraper-x.x>/src/scripts/_schedule_scrape_jobs.sh" to begin running the job scraper.
sleep 30