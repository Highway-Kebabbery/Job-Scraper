How to Use:

Download Termux from the app store
run pkg update && pkg upgrade (select default options when prompted)
run pkg install python
run pkg install python-pip
run pip install selenium beautifulsoup4

install firefox browser from app store

Move files to Termux home directory (can't move through command line due to restrictions on Termux permissions)
    install FX file explorer from the app store (recommended by Termux): https://play.google.com/store/apps/details?id=nextapp.fx
    Connect to Termux storage (pictures aren't exact but are very useful https://imgur.com/a/NDkpeaz):
        From menu, select "Connect to Storage"
        Open side-menu to select "Termux"
        Select "USE THIS FOLDER"
        Termux home directory is now available to move files to
        Downlaod project (the .tar.gz version is required for Android)
        Move downloaded project to Termux home directory
        run tar -xf <compressed project folder name>


Where I left off:
It looks like I need a file manager to be able to poke around my android phone. They make them with no rooting required. This may not be necessary for describing how to install and use the app.
I need to figure out how to have easy control over file locations on the phone so that I can troubleshoot and get everything set up.
It looks like GeckoDriver may work as is on the phone.... Or not. IDFK yet.









Learned:
If there's too much HTML, you can't print all to the console. Save to a file to see it all.
Learned about docstrings
Got to practice building Python classes


NOTES:
Have the Android notification take you to the jobs page when clicked (even when no jobs available).
HERE'S A BIG NOTE: THIS COMPARES THE OLD RESULTS TO THE NEW TO DETERMINE IF  AJOB WAS POSTED. IF THEY DELETE A JOB, IT'LL TELL ME A JOB WAS POSTED.