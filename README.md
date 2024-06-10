NOTE ABOUT checking ToS and robots.txt to see if they allow scraping.

How to Use:

second attempt
Download and install F-Droid from https://f-droid.org/en/. You may be prompted to set permissions to allow the installation of the .apk file.
Install Termux Terminal from F-Droid. DO NOT install from Google Play Store as Termux has halted updates through the Google Play Store. You may be prompted to allow app installs from this source.
Install Termux:API from F-Droid.
Go to Apps > Termux and allow it to send notifications
Go to Apps > Termux:API and allow it to send notifications
Configure Termux (Big thank you to luanon404 at https://github.com/luanon404/Selenium-On-Termux-Android?tab=readme-ov-file):
Note: Force-quit the app if it begins entering "y" in an infinite loop. It's happened to me on very rare occasions..
run: yes | pkg update -y && yes | pkg upgrade -y
run: termux-change-repo and select Mirror group. On the next page, I selected North American mirrors. Use arrow keys, space, and enter to make selections.
run: yes | pkg install python-pip -y
run: pip install selenium==4.9.1 beautifulsoup4
run: yes | pkg install x11-repo -y
run: yes | pkg install firefox -y
run: yes | pkg install geckodriver -y
run: termux-setup-storage and grant permission.
run: pkg install termux-api
download the release from my repo. You can either use the command line in Termux to move the download to the home folder (/data/data/com.termux/files/home), or you can do the following:
Move files to Termux home directory (can't move through command line due to restrictions on Termux permissions). (/data/data/com.termux/files/home)
    install FX file explorer from the app store (recommended by Termux): https://play.google.com/store/apps/details?id=nextapp.fx
    Connect to Termux storage (pictures aren't exact but are very useful https://imgur.com/a/NDkpeaz):
        From menu, select "Connect to Storage"
        Open side-menu to select "Termux"
        Select "USE THIS FOLDER"
        Termux home directory is now available to move files to
        Downlaod project (the .tar.gz version is required for Android)
        Move downloaded project to Termux home directory
run tar -xf <compressed project folder name>
    Project folder MUST be in /data/data/com.termux/files/home after extraction.


Where I left off:
It looks like I need a file manager to be able to poke around my android phone. They make them with no rooting required. This may not be necessary for describing how to install and use the app.
I need to figure out how to have easy control over file locations on the phone so that I can troubleshoot and get everything set up.
It looks like GeckoDriver may work as is on the phone.... Or not. IDFK yet.









Learned:
If there's too much HTML, you can't print all to the console. Save to a file to see it all.
Learned about docstrings
Got to practice building Python classes
Termux halted all updates on google play. Thanks Peter Mortensen on Stack Exchange. You saved my life.

NOTES:
Have the Android notification take you to the jobs page when clicked (even when no jobs available).
HERE'S A BIG NOTE: THIS COMPARES THE OLD RESULTS TO THE NEW TO DETERMINE IF  AJOB WAS POSTED. IF THEY DELETE A JOB, IT'LL TELL ME A JOB WAS POSTED.
