#!/data/data/com.termux/files/usr/bin/python

"""Loads a company's provided careers page and uses the provided tag and attribute identifier to scrape job listings.
    Careers are compared against the last scrape to determine if a change occurred and a notification is sent to the host's phone.
"""

import os
import json
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CompanyJobsFinder():
    """A class for finding and storing job listings available at a company."""

    # Scraping and job comparison
    __driver = None
    __company_name = ''
    __url = ''
    __target_tag = ''
    __target_attribute_value = ''
    __company_data_filepath = ''
    __current_jobs = []
    __previous_jobs = []

    # Sending notifications
    __new_jobs_today_msg_title = ''
    __new_jobs_yesterday_msg_title = ''
    __no_jobs_yesterday_msg_title = ''
    __notification_command = ''
    __id_counter = int()    # The index of the company in the list of companies to check. Appends to various objects to give each company a unique number so company actions don't overwrite one another.

    # filepaths
    __cd = ''
    __no_job_jpg_filepath = ''
    __job_jpg_filepath = ''
    __notification_script_filepath = ''
    __termux_shebang = '#!/data/data/com.termux/files/usr/bin/bash'

    def __init__(self, company_name, url, target_tag, target_attribute_value, id_counter):
        self.__set_firefox_driver()   # DON'T FORGET to remove the 'mobile=False' argument when you finish testing on Windows =____=
        self.__company_name = company_name
        self.__url = url
        self.__target_tag = target_tag
        self.__target_attribute_value = target_attribute_value
        self.__company_data_filepath = './data/' + str(self.__company_name) + '.json'
        self.__new_jobs_today_msg_title = f'Job listings updated today for {company_name}!'
        self.__new_jobs_yesterday_msg_title = f'Job listings updated yesterday for {company_name}!'
        self.__no_jobs_yesterday_msg_title = f'No new jobs yesterday at {company_name}.'
        self.__id_counter = id_counter
        self.__build_cd()
        self.__no_job_jpg_filepath = f'/{self.__cd}/media/no_job.jpg'
        self.__job_jpg_filepath = f'/{self.__cd}/media/job.jpg'
        self.__notification_script_filepath = f'/{self.__cd}/scripts/daily-notify-{self.__id_counter}.sh'
    
    def __set_firefox_driver(self, mobile=True):
        """Set up the web driver

        Args:
            mobile (bool, optional): I set the script/project up to run both on Win64 (for basic configuration) and on Linux
            because the script is run through Termux on Android, which provides a Linux-based environment. When troubleshooting
            on Win64, don't forget to add the <mobile=False> argument when called in __init__. Defaults to True.
        """

        if mobile == False:
            # driver is in environment variables on Android and needs not be called.
            gecko_driver_path = './drivers/win64/geckodriver.exe'
            service = FirefoxService(executable_path=gecko_driver_path)
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        if mobile == True:
            self.__driver = webdriver.Firefox(options=options)
        else:
            self.__driver = webdriver.Firefox(service=service, options=options)

    def __build_cd(self):
        """Build the filepath for the current directory of this program. Note that the forward-slashes are stripped from the end of the filepath.
        """
        cd = os.popen('pwd').read().strip()
        if cd[-1] == "/":
            cd = cd[:-1]
        if cd[0] == "/":
            cd = cd[1:]
        
        self.__cd = cd

    @property
    def company_name(self):
        """Getter for self.__company_name

        Returns:
            string: company name
        """
        return self.__company_name
    
    @property
    def url(self):
        """Getter for company careers page url.

        Returns:
            string: url for company careers page.
        """
        return self.__url

    @property
    def previous_jobs(self):
        """Getter for self.__previous_jobs

        Returns:
            .json: List of jobs as of the last search.
        """
        return self.__previous_jobs

    def set_previous_jobs(self):
        """Setter for self.__previous_jobs
        """

        # Create new file on first run for a given company.
        # Try to rewrite it as Try (open) except (make new file) else (load existing file) finally (file close) after everything else works.
        if not os.path.exists(self.__company_data_filepath):    # As I understand it, it's a security risk to test a file before opening it because it can create race conditions. That looks like a whole lot of stuff I need to read about later.
            with open(self.__company_data_filepath, 'w') as file:
                json.dump({'Titles': [], "date_json_mod": datetime.now() - timedelta(days=1), "update_detected": True}, file, indent=4, default=str)   # Setting date to yesterday on file creating creates conditions to send daily notification after day 1.
                file.close()
        
        with open(self.__company_data_filepath, 'r') as file:
            self.__previous_jobs = json.load(file)
            file.close()

    @property
    def current_jobs(self):
        """Getter for self.__current_jobs

        Returns:
            List: List of job titles currently available at the company.
        """
        return self.__current_jobs
    
    def set_current_jobs_by_class(self, child=False):
        """This is the setter method for self.__current_jobs.
        This method gets a webpage and scrapes it for jobs. It can either operate on
        tags with unique identifiers, or the immediate child of a tag with a unique identifier.

        Args:
            child (bool, optional): Sets whether you're looking in the child of the
            identifiable tag for the job information. Defaults to False.

        Returns:
            List: List of job titles currently available at the company.
        """        
        self.__driver.get(self.__url)

        # When the target element is present, scrape and parse html.
        try:
            WebDriverWait(self.__driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.__target_attribute_value))
            )
        except Exception as e:
            print(f"Failed to load job listings: {e}")
            return []
        
        html = self.__driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Locate job titles.
        tags = soup.find_all(self.__target_tag, class_=self.__target_attribute_value)
        if child == False:
            for target_tag in tags:
                self.__current_jobs.append(target_tag.string)
        else:
            # Pull the string from the child of each uniquely identifiable parent tag.
            # Only works if there's only one child.
            for parent_tag in tags:
                self.__current_jobs.append(parent_tag.find().string)
        
        self.__driver.quit()

    def dump_current_jobs_json(self, update_detected):
        """This method saves the current job listings to a .json file for comparison to the old job listings.

        Args:
            company_name (string): Used to generate filename.
            update_detected (bool): Used tomorrow to determine whether jobs were found today.
        """

        # Structure the data for .json export
        self.__current_jobs = {'Titles': self.__current_jobs}
        self.__current_jobs['date_json_mod'] = datetime.now()
        self.__current_jobs['update_detected'] = update_detected

        with open(self.__company_data_filepath, 'w') as file:
            json.dump(self.__current_jobs, file, indent=4, default=str)    # default=str tells the .json file how to handle non-serializable type, such as datetime. Should be okay here since I know exactly what's getting stored every time.
            file.close()
    
    def send_notification(self, daily_reminder=False):
        """Build and send notifications about the status of job listings at the company.

        Args:
            daily_reminder (bool, optional): Flags whether to send the single daily message summarizing yesterday's findings. Defaults to False.
        """
        # Choose content of the notification
        if daily_reminder == True:
            if self.__previous_jobs['update_detected'] == False:    # Most likely message to occur
                self.__notification_command = f'termux-notification --title "{self.__no_jobs_yesterday_msg_title}" --content "Keep eating ramen noodles." --id big_unemployed-daily-{self.__id_counter} --image-path {self.__no_job_jpg_filepath} --button1 "Dismiss" --button1-action "termux-notification-remove big_unemployed-daily-{self.__id_counter}" '
            else:
                self.__notification_command = f'termux-notification --title "{self.__new_jobs_yesterday_msg_title}" --content "Tap now to visit the {self.__company_name} careers page." --action "termux-open-url {self.__url}" --id big_employed-daily-{self.__id_counter} --image-path {self.__job_jpg_filepath} --button1 "Dismiss" --button1-action "termux-notification-remove big_employed-daily-{self.__id_counter}" '
        else:
            self.__notification_command = f'termux-notification --title "{self.__new_jobs_today_msg_title}" --content "Tap now to visit the {self.__company_name} careers page." --action "termux-open-url {self.__url}" --id big_employed-{self.__id_counter} --image-path {self.__job_jpg_filepath} --button1 "Dismiss" --button1-action "termux-notification-remove big_employed-{self.__id_counter}" '
        
        # Send the notification
        if daily_reminder == True:
            self.__build_notif_shell_script()
            self.__schedule_daily_notification()
        else:
            os.system(f'{self.__notification_command}')

    def __build_notif_shell_script(self):
        """Builds the shell script to send the daily notification at the scheduled time.
        """
        with open(self.__notification_script_filepath, 'w') as file:
            file.write(f'{self.__termux_shebang}\n')
            file.write(f'{self.__notification_command}\n')
            file.close()
        os.system(f'chmod +x {self.__notification_script_filepath}')

    def __schedule_daily_notification(self):
        """Schedule the daily notification
        """
        current_time = datetime.now()
        notification_time = current_time.replace(hour=10, minute=0, second=0, microsecond=0)

        if current_time > notification_time:
            notification_time = current_time + timedelta(days=1)    # Can't go back in time to send a notification.

        os.system('echo sv-enable atd')    # enable at daemon
        os.system('sv up atd')    # start at service for one job
        os.system(f'echo "{self.__notification_script_filepath}" | at {notification_time.strftime("%H:%M %m/%d/%Y")}')

class LogExecution():
    """A class to handle logging the execution of the program.
    """
    __number_of_companies = int()
    __execution_log_filepath = ''
    __start_time = None
    __stop_time = None
    __total_time = None

    def __init__(self, list_of_companies):
        self.__number_of_companies = len(list_of_companies)
        self.__build_cd()
        self.__log_timestamp(start=True)

    def __build_cd(self):   # This could've technically been inherited from CompanyJobsFinder or vice versa, but the classes don't seem to be in an is-a nor a has-a relationship.
        """Build the filepath for the current directory of this program. Note that the forward-slashes are stripped from the end of the filepath.
        """
        cd = os.popen('pwd').read().strip()
        if cd[-1] == "/":
            cd = cd[:-1]
        if cd[0] == "/":
            cd = cd[1:]
        
        self.__execution_log_filepath = f'/{cd}/../logs/execution_log.txt'

    def __log_timestamp(self, start=bool):
        if start == True:
            self.__start_time = datetime.now()
        else:
            self.__stop_time = datetime.now()
    
    def __calc_total_time(self):
        self.__total_time = self.__stop_time - self.__start_time

    def write_execution_txt(self):
        self.__log_timestamp(start=False)
        self.__calc_total_time()
        with open(self.__execution_log_filepath, 'a') as file:
            file.write(f'Start Time: {self.__start_time}, Stop Time: {self.__stop_time}, Total Time: {self.__total_time}, Companies Analyzed: {self.__number_of_companies}, Average Time per Company: {self.__total_time / self.__number_of_companies}\n')
            file.close()

def main():
    """
        main() builds company objects, scrapes current jobs, compares to previous jobs, and reports updates.
            * Users receive one daily update notification:
                * If an update was found yesterday, the daily notification informs the user.
                * If no updates were found, the daily notification informs the user of their continued unemployment.
            * In addition, the user is notified when a job listing update is found as well as on every subsequent run of that day to ensure visibility.
        
        To track new companies, simply create and fill out a company attributes list then add that list to the list of companies below.
    """
    
    # Company name, careers page url, target tag, target attribute, targeting child of target attribute?
    jagex = ['Jagex', 'https://apply.workable.com/jagex-limited/', 'h3', 'styles--3TJHk', True]
    companies = [jagex]

    update_detected = False
    
    # Log execution start
    execution_logger = LogExecution(companies)

    for company in companies:
        company_object = CompanyJobsFinder(company[0], company[1], company[2], company[3], companies.index(company))
        company_object.set_previous_jobs()
        company_object.set_current_jobs_by_class(child=company[4])

        if company_object.previous_jobs['Titles'] != company_object.current_jobs:
            update_detected = True
            company_object.dump_current_jobs_json(update_detected)
        
        # Send notifications
        if datetime.strptime(company_object.previous_jobs['date_json_mod'], '%Y-%m-%d %H:%M:%S.%f').date() != date.today():
            # First execution of the day prepares the daily notification.
            if company_object.previous_jobs['update_detected'] == False:
                company_object.send_notification(daily_reminder=True)
            else:
                company_object.send_notification(daily_reminder=True)
                company_object.dump_current_jobs_json(update_detected)
        else:
            # Subsequent executions only notify is a job was found either on the current execution or earlier in the same day.
            if company_object.previous_jobs['update_detected'] == True:
                company_object.send_notification()  # Index number is appended to --id attribute in termux-notification which generates a unique notification id per company so notifications don't overwrite each other.

    # Log execution finish
    execution_logger.write_execution_txt()

if __name__ == '__main__':
    main()


# Still need to set daily messages to schedule a time
"""
    Notes for what I'll call the final project:

    * Running `python scrape_jobs.py` gives the script permission to read/write the files I need (./data/<company>.json), but running `chmod +x ./path/to/scape_jobs.py` then `./path/to/scrape_jobs.py` does not give it the permission to do this.
    * completely delete termux and all dependencies to begin testing the configuration script
    * When that works, test the installation script
    * When that works, manually test the scraper.
    * When that works, test the cronjob scheduling script.
    * When that works, Make sure the scraper itself is still working, and check to see that you get your daily notification the next day.
    * Create a test unit for the entire scraper that runs on Windows to work out scraping the company of your choice before automating it.
    * When that's all done, write the README.md file
    * "Get a job you ******* slob's how he replied" (but realaly, celebrate your accomplishment)

    Notes for future work:
    * What happens if they remove all listings and there's nothing to return? I... don't know how to test and account for that until after a company I targeted removes all listings.
    * Program currently only checks whether the listings changed. This will register removals as well as new listings. Find a way to notate new listings.
    * I can probably do something like check to see if each current job is in the past jobs, and if each past job is in the current jobs.
        * If current job not in pastlistings, BOOM new listing, and I have its name and can store in a variable for use. If past job not in current listings... who cares. Maybe don't check for that after all.
    * I don't filter for keywords. This is fine for now as I'm targeting smaller companies with fewer listing updates, but for larger companies I'd want to filter new jobs by keyword.
    * I also only check for updates. I could feasibly use this class to simply check for jobs with certain keywords. For example: scrape company with many listings for jobs, then monitor over time for changes.
    * I'm going to need to handle instances where there are multiple pages of jobs. Another issue for when I target larger companies. Selenium should make it easy to handle.
"""