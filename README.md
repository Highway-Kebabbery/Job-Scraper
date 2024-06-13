NOTE ABOUT checking ToS and robots.txt to see if they allow scraping.

## How to Use

### Download Required Apps and Set Permissions:
1. On your phone, download and install F-Droid  [here](https://f-droid.org/en/). You may be prompted to set permissions to allow the installation of the .apk file.
2. Install Termux from the F-Droid app ([for reference](https://f-droid.org/en/packages/com.termux/)).
    * DO NOT install from Google Play Store as Termux has halted updates through the Google Play Store. You may be prompted to allow app installs from this source.
3. Install Termux:API from the F-Droid app ([for reference](https://f-droid.org/en/packages/com.termux.api/)).
4. Install FX File Explorer from the <u>Google Play store</u> ([for reference](https://play.google.com/store/apps/details?id=nextapp.fx)).
5. Go to "Apps" > "Termux" and allow Termux to send notifications. Do the same for Termux:API.
6. In "Apps" > "Termux," check Termux for battery-related settings and set them to "unrestricted," or otherwise to not be optimized for battery life. Do the same for Termux:API.
7. In "Settings" > "Battery," check "Background usage limits" > "Never auto sleeping apps" for any Termux related apps.
    * As of Android 14, turning off battery optimization removes them from this list, but you should still check here to make sure there's no optimization happening.


### Configure FX File Explorer:
1. Navigate to [this guide](https://imgur.com/a/NDkpeaz). The pictures aren't exact, but they're useful.
2. From the menu, select "Connect to Storage."
3. Open the side-menu and select "Termux."
4. Select "USE THIS FOLDER."
5. The Termux home directory ("home" in FX File Explorer) is now available for navigation.

### Job Scraper Download and Configuration:
1. <u>On your Android phone</u>, downlaod the .tar.gz file containing the latest release [here](https://github.com/Highway-Kebabbery/Job-Scraper/releases/).
2. Open FX File Explorer and move the compressed project file to Termux home directory.
3. Open Termux.
4. Run: `pwd`. You should be in `/data/data/com.termux/files/home/`
5. Run: `ls`. You should see the compressed project folder.
6. Run: `tar -xf <project-folder-name.tar.gz>` to extract the files here.
    * The extracted project folder MUST be in `/data/data/com.termux/files/home/` to run.
7. Run: `chmod +x ./<project-folder-name>/src/scripts/setup.sh` to give the setup script execute permissions.
8. Run: `./<project-folder-name>/src/scripts/setup.sh`.

******HEYHEYHEY HEY HEY HERE'S A NOTE. LET THEM KNOW ABOUT POTENTIAL SETUP ERROS.

A big thank you to [luanon404](https://github.com/luanon404/Selenium-On-Termux-Android?tab=readme-ov-file) for their help with getting Termux set up for selenium.

***BE SURE TO ADD A NOTE ABOUT ADDING NEW COMPANIES









Learned:
If there's too much HTML, you can't print all to the console. Save to a file to see it all.
Learned about docstrings
Got to practice building Python classes
Termux halted all updates on google play. Thanks Peter Mortensen on Stack Exchange. You saved my life.
Learned how to send a system command from a python script, capture the result, and store it in a variable for later use in the script.
Learned that os.popen('pwd').read() adds a newline character to the end which gave me a lot of trouble =___=