# <div align="center">Job Scraper</div>


## Description
This application alerts users to updates on a specified company's (or companies') careers page via notifications on their Android phone. **Note:** This application does **not** require you to root your Android phone.

## Features
### Current:
* One daily notification per company is scheduled for 1000 each day with a summary of yesterday's findings.
* When changes to a given company's careers page are detected, all subsequent executions for that day send a notification to the user's phone to increase visibility.
* The scraper is periodically scheduled as a cronjob, so the frequency can be easily changed.
* Note that the application currently only checks for *updates* to company listings, so a listing removal will trigger the "listings updated" notification.

### Planned:
I am currently only targeting smaller companies with a relatively small number of job listings that fit on one webpage. The following planned features will allow me to target larger companies which may have a vast number of listings that are unrelated to me and spread across multiple pages requiring the use of, *e.g.*, a "Next" button to navigate through.
* Detect only the addition of new jobs.
* Filter job listings by specified keywords to narrow the search.
    * As a result, notifications can contain the actual job titles available for application.
    * The drawback to this feature is that I may miss jobs that I am interested in if I do not use an expansive set of keyword filters.
    * The benefit to this feature is that I could target much larger companies.
* Navigate through careers pages with multiple pages using Selenium.
    * This will likely require implementation on a per-company basis, much as the scraper currently requires unique information to identify the job listing titles.
    * This will probably be implemented as its own method in the CompanyJobsFinder class.
* Possible: I could conceivably condense all available listings at all tracked companies into one text file that is built daily and linked to in the daily notification.
    * This would be useful if I am tracking so many companies that receiving one notification per company is cumbersome. It would be nice, but it is not the most important feature to work on right now.

## How to Use

### Software Requirements
* Android 14
    * Untested on other versions.
* Termux App
    * MUST be downloaded from F-Droid. The Google Play Store version is no longer supported, does not even contain all required packages, and thus will not function.
* Python 3.11.9
    * Untested on other versions.
* Selenium 4.9.1
    * Other versions untested. This version was specifically recommended, without reason, by the resource I used to get Selenium working.
    * Thank you to [luanon404](https://github.com/luanon404/Selenium-On-Termux-Android?tab=readme-ov-file) for their help with getting Selenium set up for Termux.

### Initial Setup:
#### Download Required Apps and Set Permissions:
1. On your phone, download and install F-Droid  [here](https://f-droid.org/en/).
    * You may be prompted to set permissions to allow the installation of the .apk file.
2. Install Termux from the F-Droid app ([for reference](https://f-droid.org/en/packages/com.termux/)).
    * DO NOT install Termux from the from Google Play Store as Termux has halted updates through the Google Play Store.
    * You may be prompted to allow app installs from this source.
3. Install Termux:API from the F-Droid app ([for reference](https://f-droid.org/en/packages/com.termux.api/)).
4. Install FX File Explorer from the <u>Google Play store</u> ([for reference](https://play.google.com/store/apps/details?id=nextapp.fx)).
5. Navigate to `Settings > Apps > Termux` and allow Termux to send notifications. Do the same for Termux:API.
6. Navigate to `Settings > Apps > Termux` and check Termux for battery-related settings and set them to "unrestricted," or otherwise to not be optimized for battery life. Do the same for Termux:API.
7. Navigate to `Settings > Apps > three-dot menu > Special Access > All files access > FX` and enable access.
8. In `Settings > Battery`, check `Background usage limits > Never auto sleeping apps` for any Termux related apps.
    * As of Android 14, turning off battery optimization removes them from this list, but you should still check here to make sure there is no optimization happening.

#### Configure FX File Explorer:
If you have trouble, you may optionally check out [this guide](https://imgur.com/a/NDkpeaz). The pictures are not exact, but they are useful.
1. Open Termux and give it a second to install the bootstrap packages. You can exit the app afterwards.
2. Open FX File Explorer.
3. There may be a warning message at the bottom stating that FX needs access to read/write files etc. in order to function. Select `ENABLE ACCESS`.
4. Open the three-dots menu and select `Connect to Storage`.
5. Open the three-lines menu and select `Termux`.
6. Select `USE THIS FOLDER`. Allow FX to access files in Termux.
7. Return to the FX File Explorer home page. The Termux `home` directory is now available for navigation.

#### Job Scraper Download and Configuration:
1. <u>On your Android phone</u>, downlaod the .tar.gz file containing the latest release [here](https://github.com/Highway-Kebabbery/Job-Scraper/releases/).
2. In FX File Explorer, locate the compressed project file inside `Download`. Move the compressed project file to the Termux home directory.

    <img src="./docs/images/termux-home-dir.jpg" alt="Demonstration of Termux home folder within FX File Explorer" width="200"/>

3. Open Termux.
4. Ensure you are in `/data/data/com.termux/files/home/`.
5. Run: `ls`. You should see the compressed project folder.
    * Note: You should only have one version of the project downloaded at any given time. Remove old versions before upgrading.
6. Run: `tar -xf Job-Scraper-<version number>.tar.gz` to extract the files here.
    * The extracted project folder MUST be in `/data/data/com.termux/files/home/` to run.
7. Run: `chmod 700 Job-Scraper-<version number>` to set permissions.
8. Run: `./Job-Scraper-<version number>/src/scripts/_setup.sh` to configure Termux to run the job scraper.
9. When setup finishes, COMPLETELY exit Termux. To do so, use the `Exit` option in the Termux persistent notification.

    <img src="./docs/images/termux-exit.jpg" alt="Termux 'Exit' option shown in the persisten notification." width="200"/>

10. Setup is complete once Termux has been completely exited.

### Operation:
1. Executing the script:
    * Open Termux, ensure you are in the home directory, and run `./Job-Scraper-<version number>/Schedule_Job_Scraper.sh`.
    * To check whether the job was started, run `crontab -l`.
    * To stop the job, run `crontab -r`.
    * The application is designed to treat the first day of scraping a company website as a positive listing update identification, so it will send a notification on each subsequent execution that day.
2. Adding companies to track:
    * Check robots.txt before scraping a website and respect the owner's preferences.
    * $$$$$$$$$$$$$$$$$$$$$$$$$$$
3. Changing execution frequency:
    * $$$$$$$$$$$$$$$$$$$$$$$$$$$


## Technology
* **Python:** I chose Python for several reasons:
    * It is an appropriate tool for the job when considering both the language and the available libraries (namely, Selenium and Beautiful Soup).
    * Having experience in these libraries will likely be valuable for me as an employee in the future.
    * I know it.
    * **Selenium:** Selenium was required to deal with dynamically loaded webpages. It allows me to wait to collect the html until everything I need has loaded, and it is also a widely used and well-vetted tool for this job.
    * **Beautiful Soup:** Beautiful Soup is a widely-used library for parsing html. 
* **Termux:** Termux is an emulated command line providing a Linux environment on an Android phone. I chose to implement this application with Termux because it has tools to execute functions like periodic background execution and scheduling, it does not require rooting the Android device, and, though I did have a lot to learn about using the Linux functions available on Termux, I did not need to learn about native Android development. Furthermore, using Termux allowed me to hsot this application on my phone, which means that I do not need to leave my computer on 24/7 to run such a simple task. It is incredibly convenient.
    * **`cronie`:** The `cron(ie)` package allows for *periodic* scheduling of tasks. *i.e.* Executing the web scraper every *n* hours.
    * **`at`:** The `at` package allowed me to easily schedule daily notifications to occur once at 1000, and subsequently to clean up the shell scripts with instructions to send those notifications.
* **Bash:** Bash shell scripts were used to interact with the command line. I used them automate the setup of the Termux environment upon installation, to set up the cronjob that runs the application, and to store instructions for notifications to be executed after the python script finished executing.
* **JSON:** .json files were a natural choice for storing the results of each execution for comparison at a later time.


## What I Learned
The most challenging parts of this project were related to the configuration of the emulated Linux environment running on an Android phone.

**Python**:
* 

**Termux (Linux environment):**
* 

**Shell:**
* 

**General:**
* 


## Motivation
I created this application for two reasons.
1. I want to be a software engineer and will need a job soon. This application will help me monitor companies that I am interested in for jobs I am qualified to apply to. It also serves as a portfolio piece for said jobs.
    * "Hello, Highway Kebabbery, we are not the slightest bit concerned that you built a program to stalk our careers page on a three-hourly basis day and night in the hopes of finding employment here. That does not put us off at all. Please come in for your interview."
2. I used to bot on Runescape. I found it rather enjoyable to tweak the code in the bots I found to try and improve their performance. One simple tactic I employed was to add a randomization fucntion for every mouseclick command so as to avoid their macro detection system. After much success, my confidence ballooned and my meticulous tendencies began to slip. Ultimately, I tested one bot for too long without the click randomization function and my childhood account was banned. I made a very rational and contrite appeal to Jagex four years later, but I was denied. It was very unfair /s. As such, my tertiary life-goal is to infiltrate Jagex by gaining so much experience that I would be impossible to turn down for a job. I am going to make them an offer they cannot refuse. Once I am hired at Jagex, at some indeterminate point in the future, and in a role with write access to their database, then I am going to `UPDATE player_accounts SET banned = 'F' WHERE account_name = '<my_account_name>'`.






MAIN WORK OUTSTANDING:
* Continue testing background functionality of cronjob
* Fix -setup.sh so that it always functions completely and perfectly. Wth is wrong with it?
* Finish README





******HEYHEYHEY HEY HEY HERE'S A NOTE. LET THEM KNOW ABOUT POTENTIAL SETUP ERROS.
*****Note: Force-quit the app if it begins entering "y" in an infinite loop. It's happened to me on very rare occasions.
Note about having mirror groups for NA, SA, and Europe. Recommend reordering them based on location.

***Will need to add screen recording of the app working when it's all running in the final implementation.

****Pore through scrape_jobs.py and write down everything I've learned.
****Remember to get video of daily notification coming in and taking you to job site.
****Last two notifications (per-execution and daily) didn't take me to job site? Why no work anymore??


Learned:
If there's too much HTML, you can't print all to the console. Save to a file to see it all.
Learned about docstrings
Got to practice building Python classes
Termux halted all updates on google play. Thanks Peter Mortensen on Stack Exchange. You saved my life.
Learned how to send a system command from a python script, capture the result, and store it in a variable for later use in the script.
Learned that os.popen('pwd').read() adds a newline character to the end which gave me a lot of trouble =___=
somewhere, I need to link to this release version to show that I can outline software testing https://github.com/Highway-Kebabbery/Job-Scraper/releases/tag/v0.4.1
writing to external file for troubleshooting when process runs (fails) in background
Learned how to write out to external files through terminal when my program fails in the background
A lot of shell scripting experience

**Termux/Linux:**
* How to update the Termux source repository/mirrors.
* How to configure the Termux environment to run Python, Selenium, and Beautiful Soup.* How to set permissions for files and directories.
* How to make a script executable with a shebang.
* How to configure the Termux environment to run cronjobs and `at` jobs (as well as how to use these features on Linux).
* `cron`:
    * How to run a cronjob
    * How to push crontab to a file and back for controlled editing
    * Learned that `cron` runs out of a different directory than when a script is executed manually. Set filepaths accordingly.
* How to schedule a job with `at`.

**Python:**
* I finally got a chance to show that I generally know Python; I just haven't had an extensive use for it yet.
    * I had no need to make Pythonic setters. Any attribute values passed between classes were required in __init__(), so I simply passed them as arguments during instantiation rather than create @property.setter methods. None of them will ever be updated after instantiation.
    * Learned about docstrings.
* Practice using Python to send commands out to the command line and receive data back to be stored in a variable.
* Experience using .json files to store data for use in later executions.
* Experience writing to .csv files to log execution data.
* Learned about web scraping:
    * Learned about robots.txt.
    * More practice with Selenium.
    * Learned how to use Beautiful Soup to parse html.
    
**Debugging:**
* Much time spent using Python to write data out to text files to help me debug processes running in the background that I could not see.
* Practice reducing processes to their most simple form to help identify what is broken.
    * To be fair, I've spent my entire life and career doing this, but I kind of need prospective software employers to know that I know this...

**General:**
* Experience with project design.
    * What tools will I need, and which options are best suited for the job?
    * What is required to get these tools set up and running for my project? How do I trust that the tools are set up properly?
    * How do I know whether my script is failing or the dependencies are causing the issue?
    * How do I organize this process into a coherent set of instructions for new users to follow? What problems can I help them anticipate and avoid?