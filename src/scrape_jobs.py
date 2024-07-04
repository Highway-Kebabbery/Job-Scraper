#!/data/data/com.termux/files/usr/bin/python

"""
    Features:
    main() builds company objects, scrapes current jobs, compares to previous jobs, and reports updates.
        * Users receive one daily update notification:
            * If an update was found yesterday, the daily notification informs the user.
            * If no updates were found, the daily notification informs the user of their continued unemployment.
        * In addition, when a listing update is detected, the user receives a per-execution notification on every subsequent run of the day to ensure visibility.
    
    desktop_scraper() is a version of main() that's been stripped down for Windows-64 systems. It is used to easily test which attributes work for scraping new commpany job pages.
        
    View the main() or desktop_scraper() docstrings for more detailed information.
"""

import os
import json
import csv
import time
from collections import Counter
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ThisExecution():
    """This class contains general data about the execution to be passed to other classes.
    """
    project_version = ''
    wd = ''
    mobile = bool()
    fast_notifications = bool()

    def __init__(self, project_version=project_version, mobile=True, fast_notifications=False):
        """_summary_

        Args:
            project_version (string): Release version. Used to build exact filepaths.
            mobile (bool, optional): Used to decide how to find the location of geckodriver, as this differs from Termux (mobile) to Windows. Defaults to True.
            fast_notifications (bool, optional): Used to send daily notifications one minute after generation for quick testing. Defaults to False.
        """
        self.project_version = project_version
        self.mobile = mobile
        self.fast_notifications = fast_notifications
        self.__build_wd()

    def __build_wd(self):
        """
            Build the filepath for the current directory of this program. Note that the forward-slashes are stripped from the end of the filepath.
        """
        wd = os.popen('pwd').read().strip()
        if wd[-1] == "/":
            wd = wd[:-1]
        if wd[0] == "/":
            wd = wd[1:]
        
        self.wd = wd

class CompanyJobsFinder():
    """A class for finding and storing job listings available at a company."""

    # Scraping and job comparison
    __gecko_driver_path = ''
    __driver = None
    __company_name = ''
    __url = ''
    __job_title_tag = ''
    __job_title_tag_attr_val = ''
    __company_data_filepath = ''
    __current_jobs = []
    __previous_jobs = []
    __title_class_by_selector = None
    __loads_by_page = bool()
    __show_more_button_text = ''

    # Notification content
    __new_jobs_today_msg_title = ''
    __new_jobs_yesterday_msg_title = ''
    __no_jobs_yesterday_msg_title = ''
    __notification_command = ''
    __fast_notifications = bool()

    # filepaths
    __wd = ''
    __project_version = ''
    __no_job_jpg_filepath = ''
    __job_jpg_filepath = ''
    __notification_script_filepath = ''
    __bash_shebang = '#!/data/data/com.termux/files/usr/bin/bash'

    def __init__(self, company_name, url, job_title_tag, class_by_selector, job_title_tag_attr_val, loads_by_page, show_more_button_text, wd, project_version, mobile, fast_notifications):
        self.__set_firefox_driver(mobile)
        self.__company_name = company_name
        self.__url = url
        self.__job_title_tag = job_title_tag
        self.__job_title_tag_attr_val = job_title_tag_attr_val
        self.__loads_by_page = loads_by_page
        self.__show_more_button_text = show_more_button_text
        
        # Use the attribute that identifies the job title tag to set the Selenium `By` method to be called.
        match class_by_selector:
            case 'id':
                self.__title_class_by_selector = By.ID
            case 'name':
                self.__title_class_by_selector = By.NAME
            case 'xpath':
                self.__title_class_by_selector = By.XPATH
            case 'link text':
                self.__title_class_by_selector = By.LINK_TEXT
            case 'partial link text':
                self.__title_class_by_selector = By.PARTIAL_LINK_TEXT
            case 'tag name':
                self.__title_class_by_selector = By.TAG_NAME
            case 'class name':
                self.__title_class_by_selector = By.CLASS_NAME
            case 'css selector':
                self.__title_class_by_selector = By.CSS_SELECTOR
            case _:
                print('Invalid class_by_selector argument passed to CompanyJobsFinder.0')
                raise SystemExit

        # Configure notification parameters
        self.__new_jobs_today_msg_title = f'Job listings updated today for {company_name}!'
        self.__new_jobs_yesterday_msg_title = f'Job listings updated yesterday for {company_name}!'
        self.__no_jobs_yesterday_msg_title = f'No new jobs yesterday at {company_name}.'
        self.__fast_notifications = fast_notifications

        # Build file paths
        self.__project_version = project_version
        self.__wd = wd
        self.__gecko_driver_path = f'/{self.__wd}/src/drivers/win64/geckodriver.exe'
        self.__company_data_filepath = f'/{self.__wd}/Job-Scraper-{self.__project_version}/src/data/{self.__company_name}.json'
        self.__no_job_jpg_filepath = f'/{self.__wd}/Job-Scraper-{self.__project_version}/src/media/no_job.jpg'
        self.__job_jpg_filepath = f'/{self.__wd}/Job-Scraper-{self.__project_version}/src/media/job.jpg'
        self.__notification_script_filepath = f'/{self.__wd}/Job-Scraper-{self.__project_version}/src/scripts/daily_notify_{company_name}.sh'
    
    def __set_firefox_driver(self, mobile=True):
        """Set up the web driver

        Args:
            mobile (bool, optional): I set the script/project up to run both on Win64 (for basic configuration) and on Linux
            because the script is run through Termux on Android, which provides a Linux-based environment. When troubleshooting
            on Win64, don't forget to add the <mobile=False> argument when called in __init__. Defaults to True.
        """
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        if mobile == True:
            # driver is in environment variables on Android and needs not be called.
            self.__driver = webdriver.Firefox(options=options)
        else:
            service = FirefoxService(executable_path=self.__gecko_driver_path)
            self.__driver = webdriver.Firefox(service=service, options=options)
            
    @property
    def previous_jobs(self):
        """Getter for self.__previous_jobs

        Returns:
            Dict: List of jobs as of the last search, time of last execution, whether an update has been detected today.
        """
        return self.__previous_jobs

    def set_previous_jobs(self):
        """Setter for self.__previous_jobs
        """
        # Checking for the file like this avoids potentially creating race conditions... something I stumbled upon and now need to go read about.
        try:
            with open((self.__company_data_filepath), 'r') as file:
                pass
        except FileNotFoundError:
            if self.__fast_notifications == False:
                self.__previous_jobs = {'Titles': [], "date_json_mod": str(datetime.now()), "update_detected": True}
            else:
                # For testing the daily notification. Setting the date to yesterday upon file creation creates conditions to prepare the daily notification script immediately.
                self.__previous_jobs = {'Titles': [], "date_json_mod": str(datetime.now() - timedelta(days=1)), "update_detected": True}
        else:
            with open(self.__company_data_filepath, 'r') as file:
                self.__previous_jobs = json.load(file)
                file.close()

    @property
    def current_jobs(self):
        """Getter for self.__current_jobs

        Returns:
            List of strings: List of job titles currently available at the company. This class attribute is converted to a dictionary later, so be aware of its type and contents when you intend to call it.
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
            List of strings: List of job titles currently available at the company.
        """        
        self.__driver.get(self.__url)

        # When the target element is present, scrape and parse html.
        try:
            WebDriverWait(self.__driver, 10).until(
                EC.presence_of_element_located((self.__title_class_by_selector, self.__job_title_tag_attr_val))
            )
        except Exception as e:
            # This is where I'll put logic to handle the event where all jobs have been removed and none are available.
            # I can set logic in main()/desktop_scraper() to check whether current_jobs is empty, and if so I can just schedule the daily failure notification?
            return []
        else:
            def scrape_job_titles():
                html = self.__driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # Locate job titles.
                # It would be nice to figure out how to flexibly pass in a kwarg that matches self.__title_class_by_selector.
                # When I can do that, I can change method name to set_current_jobs, because one method handles all possible attributes I could use.
                # I'll do that later... I need to get the "show more" button feature working first.
                tags = soup.find_all(self.__job_title_tag, class_=self.__job_title_tag_attr_val)
                if child == False:
                    for job_title_tag in tags:
                        self.__current_jobs.append(job_title_tag.string)
                else:
                    # Pull the string from the child of each uniquely identifiable parent tag.
                    # Only works if there's only one child.
                    for parent_tag in tags:
                        self.__current_jobs.append(parent_tag.find().string)
            
            def click_button():
                try:
                    button = WebDriverWait(self.__driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f'//button[text()="{self.__show_more_button_text}"]'))
                    )
                    self.__driver.execute_script('arguments[0].scrollIntoView(true);', button)
                    self.__driver.execute_script('arguments[0].click();', button)
                    time.sleep(2)
                    return True
                except:
                    return False
            
            if self.__loads_by_page:
                # When jobs are shown one page at a time: scrape jobs, click next, and repeat until all pages are scraped
                scrape_job_titles()
                while True:
                    if not click_button():
                        break
                    scrape_job_titles()
            else:
                # If jobs are all shown on one page when a "show more" button is clicked, then click until it's gone and then scrape all jobs at once.
                while click_button():
                    pass
                scrape_job_titles()
        finally:
            self.__driver.quit()

    def dump_current_jobs_json(self, update_detected):
        """This method saves the current job listings to a .json file for comparison to the old job listings.

        Args:
            update_detected (bool): Used tomorrow to store whether jobs were found today.
        """
        json_formatted_data = {'Titles':self.__current_jobs, 'date_json_mod':datetime.now(), 'update_detected':update_detected}

        def write_json():
            with open(self.__company_data_filepath, 'w') as file:
                    json.dump(json_formatted_data, file, indent=4, default=str)    # default=str tells the .json file how to handle non-serializable type, such as datetime. Should be okay here since I know exactly what's getting stored every time.
                    file.close()

        try:
            with open(self.__company_data_filepath, 'r') as file:
                pass
        except FileNotFoundError:
            # The initial creation/writing to the .json has weird recursive effects in Termux. Writing to it twice fixes it... Windows functions as expected.
            for i in range(2):
                write_json()
        else:
            write_json()
    
    def send_notification(self, daily_reminder=False):
        """Build and send notifications about the status of job listings at the company.

        Args:
            daily_reminder (bool, optional): Flags whether to send the single daily message summarizing yesterday's findings. Defaults to False.
        """
        # Choose content of the notification
        if daily_reminder == True:
            if self.__previous_jobs['update_detected'] == False:    # Most likely message to occur
                self.__notification_command = f'termux-notification --title "{self.__no_jobs_yesterday_msg_title}" --content "Keep eating ramen noodles." --id big_unemployed-daily-{self.__company_name} --image-path {self.__no_job_jpg_filepath} --button1 "Dismiss" --button1-action "termux-notification-remove big_unemployed-daily-{self.__company_name}" '
            else:
                self.__notification_command = f'termux-notification --title "{self.__new_jobs_yesterday_msg_title}" --content "Tap now to visit the {self.__company_name} careers page." --action "termux-open-url {self.__url}" --id big_employed-daily-{self.__company_name} --image-path {self.__job_jpg_filepath} --button1 "Dismiss" --button1-action "termux-notification-remove big_employed-daily-{self.__company_name}" '
        else:
            self.__notification_command = f'termux-notification --title "{self.__new_jobs_today_msg_title}" --content "Tap now to visit the {self.__company_name} careers page." --action "termux-open-url {self.__url}" --id big_employed-{self.__company_name} --image-path {self.__job_jpg_filepath} --button1 "Dismiss" --button1-action "termux-notification-remove big_employed-{self.__company_name}" '
        
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
            file.write(f'{self.__bash_shebang}\n\n{self.__notification_command}\n\n')
            file.close()
        os.system(f'chmod 700 {self.__notification_script_filepath}')

    def __schedule_daily_notification(self):
        """Schedule the daily notification
        """
        if self.__fast_notifications == False:
            notification_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        else:
            # __fast_notifications allows for quick testing of daily notifications.
            notification_time = datetime.now() + timedelta(minutes=1)

        os.system('sv-enable atd')    # enable at daemon
        os.system('sv up atd')    # start at service for one job
        os.system(f'echo "{self.__notification_script_filepath}" | at {notification_time.strftime("%H:%M %m/%d/%Y")}')
        os.system(f'echo "rm {self.__notification_script_filepath}" | at {(notification_time + timedelta(minutes=1)).strftime("%H:%M %m/%d/%Y")}')    # Clean up script after use

class LogExecution():
    """A class to handle logging the execution of the program.
    """
    __number_of_companies = int()
    __wd = ''
    __project_version = ''
    __execution_log_filepath = ''
    __start_time = None
    __stop_time = None
    __total_time = None
    __time_per_company = float()

    def __init__(self, number_of_companies, wd, project_version):
        self.__number_of_companies = number_of_companies
        self.__wd = wd
        self.__project_version = project_version

    def log_timestamp(self, start=bool):
        if start == True:
            self.__build_execution_log_filepath()
            self.__start_time = datetime.now()
        else:
            self.__stop_time = datetime.now()
            self.__calc_total_time()
            self.__time_per_company = self.__total_time / self.__number_of_companies
            self.__write_execution_txt()

    def __build_execution_log_filepath(self):
        self.__execution_log_filepath = f'/{self.__wd}/Job-Scraper-{self.__project_version}/logs/execution_log.csv'

    def __calc_total_time(self):
        self.__total_time = self.__stop_time - self.__start_time

    def __write_execution_txt(self):
        csv_data = [self.__start_time, self.__stop_time, self.__total_time, self.__number_of_companies, self.__time_per_company]
        
        try:
            with open(self.__execution_log_filepath, 'r', newline='') as file:
                pass
        except FileNotFoundError:
            headers = ['Start Time', 'Stop Time', 'Total Time', 'Companies Analyzed', 'Average Time per Company']
            with open(self.__execution_log_filepath, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerow(csv_data)
                file.close()
        else:
            with open(self.__execution_log_filepath, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(csv_data)
                file.close()

def main():
    """
        Features:
        main() builds company objects, scrapes current jobs, compares to previous jobs, and reports updates.
            * Users receive one daily update notification:
                * If an update was found yesterday, the daily notification informs the user.
                * If no updates were found, the daily notification informs the user of their continued unemployment.
            * In addition, when a listing update is detected, the user receives a per-execution notification on every subsequent run of the day to ensure visibility.
        
        desktop_scraper() is a version of main() that's been stripped down for Windows-64 systems. It is used to easily test which attributes work for scraping new commpany job pages.
            
        How to use:
        * To track new companies:
            * Check the company's robots.txt and respect their wishes.
            * Comment out the main() entry point and uncomment the desktop_scraper() entry point.
            * Follow the instructions in the desktop_scraper() docstring to test the scraper on new companies.
            * In main(), create and fill out a new company attributes list and then add that list's name to `companies`.
        * No two companies should have the same name in the first position of their attribute list.
        * Instantiating `this_execution`:
            * Always make sure the version number matches the release number you're using.
            * Set fast_notifications=True when notifications are needed quickly for testing.
    """
    
    # Company details
    '''
    example_company_name = [
        'unique_company_name' (not used for any other company in the `companies` list),
        'careers_page_url' (the web page containing job listings),
        'html_tag_containing_job_title' (the tag or parent of the tag containing the job titles),
        does_child_of_targeted_tag_contain_job_title_Boolean (sometimes job titles live inside indistinct tags that are children of uniquely targetable tags - is this the case, True or False?),
        'name_of_attribute_used_for_job_title_tag_selection' (name of attribute used to uniquely select job title tag (e.g. 'id', 'name', 'xpath', 'link text', 'partial link text', 'tag name', 'class name', 'css selector')),
        'unique_job_title_tag_attr_val' (a unique attribute for targeting job title tags),
        do_job_titles_load_by_individual_pages_Boolean (i.e. Is there a button like "show next" that loads one page at a time, only displaying some of the job titles (True), or is there a button like "show more" that, when clicked, displays all previously visible job titles **and** a new set of titles all at once after being clicked (False)?),
        'show_more/next_button_text' (button text for the button that scrolls between jobs)
    ]
    '''
    jagex = ['Jagex', 'https://apply.workable.com/jagex-limited/', 'h3', True, 'class name', 'styles--3TJHk', False, 'Show more']
    companies = [jagex]

    # Validate that no two companies 'n' have the same name in companies[n][0].
    company_names = [company[0] for company in companies]
    counter = Counter(company_names)
    duplicate_names = [i for i, j in counter.items() if j > 1]
    if duplicate_names == True:
        raise SystemExit

    # Begin execution
    this_execution = ThisExecution(
        project_version='0.4.3',
        mobile=True,
        fast_notifications=False
        )
    execution_logger = LogExecution(
        len(companies),
        this_execution.wd,
        this_execution.project_version
        )
    execution_logger.log_timestamp(start=True)
    update_detected = False

    for company in companies:
        company_object = CompanyJobsFinder(
            company[0],
            company[1],
            company[2],
            company[3],
            company[5],
            company[6],
            company[7],
            this_execution.wd,
            this_execution.project_version,
            this_execution.mobile,
            this_execution.fast_notifications
            )
        
        # Compare current jobs to last execution's findings
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
    execution_logger.log_timestamp(start=False)

def desktop_scraper():
    """
        desktop_scraper() is a version of main() that's been stripped down for Windows-64 systems. It is used to easily test which attributes work for scraping new commpany job pages.

        How to use:
            * Check the company's robots.txt and respect their wishes.
            * Comment out the main() entry point and uncomment the desktop_scraper() entry point.
            * Excute the script from the parent project folder, otherwise the path will be built incorrectly.
            * The script needs to be executed from the terminal; the VS Code debugger won't work.
            * Inspect the company job listings webpage to lcoate the appropriate html tag and attribute value.
            * Fill out `new_company` with the relevant information.
            * Execute the script from the command line.
            * When testing is complete, return to main and update the company details section.
            * Be sure to uncomment main() and re-comment desktop_scraper() when finished.
    """
    
    # Company details
    '''
    example_company_name = [
        'unique_company_name' (not used for any other company in the `companies` list),
        'careers_page_url' (the web page containing job listings),
        'html_tag_containing_job_title' (the tag or parent of the tag containing the job titles),
        does_child_of_targeted_tag_contain_job_title_Boolean (sometimes job titles live inside indistinct tags that are children of uniquely targetable tags - is this the case, True or False?),
        'name_of_attribute_used_for_job_title_tag_selection' (name of attribute used to uniquely select job title tag (e.g. 'id', 'name', 'xpath', 'link text', 'partial link text', 'tag name', 'class name', 'css selector')),
        'unique_job_title_tag_attr_val' (a unique attribute for targeting job title tags),
        do_job_titles_load_by_individual_pages_Boolean (i.e. Is there a button like "show next" that loads one page at a time, only displaying some of the job titles (True), or is there a button like "show more" that, when clicked, displays all previously visible job titles **and** a new set of titles all at once after being clicked (False)?),
        'show_more/next_button_text' (button text for the button that scrolls between jobs)
    ]
    '''
    new_company = ['Jagex', 'https://apply.workable.com/jagex-limited/', 'h3', True, 'class name', 'styles--3TJHk', False, 'Show more']
    companies = [new_company]

    # Begin execution
    this_execution = ThisExecution(mobile=False)

    for company in companies:
        company_object = CompanyJobsFinder(
            company[0],
            company[1],
            company[2],
            company[4],
            company[5],
            company[6],
            company[7],
            this_execution.wd,
            this_execution.project_version,
            this_execution.mobile,
            this_execution.fast_notifications
            )

        company_object.set_current_jobs_by_class(child=company[4])
        print(company_object.current_jobs)       

if __name__ == '__main__':
    #main()
    desktop_scraper()    # Used to test the web-scraper in isolation on Windows when trying to scrape new companies.

"""
Notes for future work:
* I've accounted for this in the README, but will leave this section for future notes while working on the script.
"""

# WHEN I PICK BACK UP: Focus on getting the show next/more button functionality added.
# I can worry about making the .find_all() kwarg flexible later.

'''
    loads_by_page: bool flag to determine whether the site's button shows all jobs (i.e. "Show more" functionality) or whether it shows next page
        If all are shown, then click button until it no longer exists.
        If one page is shown, then scrape the jobs, click "show next," and repeat until "Show next" doesn't exist.
    button_tag: str variable to identify the tag out button is contained in
    button_tag_attr_val: str variable with the show more/next button's unique id

    I think I should rework set_jobs_by_class such that it is actually just a selection with inner loops to handle the loads_by_pages cases. Each of those
    selection paths would run a new method, scrape_titles, as appropriate. scrape_titles will be the existing logic of set_jobs_by_class.
    Further, I should 

    See __set_current_jobs_by_class (before reworking old logic into __scrape_titles). Figure out how to flexibly choose a kwarg_ that matches __title_class_by_selector.

    I need a company that has discrete pages of jobs ("show next") to test that functionality.

    If this works, then I need to make the by.selector and attribute value for the "show more/next" button flexible because it's currently hard-coded for writing purposes.
'''