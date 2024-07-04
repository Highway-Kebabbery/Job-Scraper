#!/data/data/com.termux/files/usr/bin/bash

setup_mirrors() {
    local repo_file="$PREFIX/etc/apt/sources.list"
    echo -e \n\n\nSetting up mirrors...\n\n\n
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
    echo -e \n\n\nMirrors set up successfully.\n\n\n
}

# Initial configuration
echo -e \n\n\nStarting initial configuration...\n\n\n
yes | pkg update -y || { echo -e \n\n\nFailed to update packages.\n\n\n; exit 1; }
yes | pkg upgrade -y || { echo -e \n\n\nFailed to upgrade packages.\n\n\n; exit 1; }
setup_mirrors
echo -e \n\n\nCompleted initial configuration.\n\n\n

echo -e \n\n\nInstalling Termux dependencies...\n\n\n
yes | pkg install termux-api cronie at python-pip x11-repo firefox geckodriver -y || { echo -e \n\n\nFailed to install Termux dependencies.\n\n\n; exit 1; }
echo -e \n\n\nTermux dependencies installed.\n\n\n

echo -e \n\n\nInstalling Python dependencies...\n\n\n
pip install selenium==4.9.1 beautifulsoup4 || { echo -e \n\n\nFailed to install Python dependencies.\n\n\n; exit 1; }
echo -e \n\n\nPython dependencies installed.\n\n\n

rm -r Job-Scraper-*.tar.gz || { echo -e \n\n\nFailed to remove old .tar.gz file.\n\n\n; exit 1; }

termux-setup-storage || { echo -e \n\n\nFailed to set up Termux Storage permissions.\n\n\n; exit 1; }    # Technically optional. Gives Termux ability to see device storage folder. Need to completely exit Termux to complete setup.
yes | pkg install termux-services -y || { echo -e \n\n\nFailed to install termux-services.\n\n\n; exit 1; }    # YOU HAVE TO FULLY EXIT THE APP AFTER INSTALLING TERMUX-SERVICES.

echo -e \n\n!!!!!!!\n
echo -e ATTENTION: Termux requires a full restart. Completely EXIT the app now.\n
echo -e !!!!!!!\n\n
echo -e Upon restart, execute './Job-Scraper-<version number>/Schedule_Job_Scraper.sh to begin running the job scraper.'
sleep 30