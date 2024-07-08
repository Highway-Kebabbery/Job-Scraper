#!/data/data/com.termux/files/usr/bin/python

"""
    Features:
    main() builds company objects, scrapes current jobs, compares to previous jobs, and reports the detection of new jobs.
        * Users receive one daily update notification:
            * If a new job was found yesterday, the daily notification informs the user.
            * If no new jobs were found, the daily notification informs the user of their continued unemployment.
        * In addition, when a new listing is detected, the user receives a per-execution notification on every subsequent run of the day to ensure visibility.
    
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ThisExecution():
    """This class contains general data about the execution to be passed to other classes.
    """

    def __init__(self, project_version='', fast_notifications=False):
        """_summary_

        Args:
            project_version (string): Release version. Used to build exact filepaths.
            fast_notifications (bool, optional): Used to send daily notifications one minute after generation for quick testing. Defaults to False.
        """
        self.project_version = project_version
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

    __bash_shebang = '#!/data/data/com.termux/files/usr/bin/bash'

    def __init__(self, company_name, url, job_title_tag, class_by_selector, job_title_tag_attr_val, loads_by_page, show_more_button_text, wd, project_version, fast_notifications):
        self.__company_name = company_name
        self.__url = url
        self.__job_title_tag = job_title_tag
        self.__job_title_tag_attr_val = job_title_tag_attr_val
        self.__current_jobs = []
        self.__previous_jobs = []
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
        self.__new_jobs_today_msg_title = f'New job found today at {company_name}!'
        self.__new_jobs_yesterday_msg_title = f'New job found yesterday at {company_name}!'
        self.__no_jobs_yesterday_msg_title = f'No new jobs yesterday at {company_name}.'
        self.__fast_notifications = fast_notifications

        # Build file paths
        self.__project_version = project_version
        self.__wd = wd
        self.__company_data_filepath = f'/{self.__wd}/Job-Scraper-{self.__project_version}/src/data/{self.__company_name}.json'
        self.__no_job_jpg_filepath = f'/{self.__wd}/Job-Scraper-{self.__project_version}/src/media/no_job.jpg'
        self.__job_jpg_filepath = f'/{self.__wd}/Job-Scraper-{self.__project_version}/src/media/job.jpg'
        self.__notification_script_filepath = f'/{self.__wd}/Job-Scraper-{self.__project_version}/src/scripts/daily_notify_{company_name}.sh'
        
        self.__set_firefox_driver()

    def __set_firefox_driver(self):
        """Set up the web driver"""

        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        self.__driver = webdriver.Firefox(options=options)
            
    @property
    def previous_jobs(self):
        """Getter for self.__previous_jobs

        Returns:
            Dict: List of jobs as of the last search, time of last execution, whether a new job has been detected today.
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
                self.__previous_jobs = {'Titles': [], "date_json_mod": str(datetime.now()), "new_job_detected": True}
            else:
                # For testing the daily notification. Setting the date to yesterday upon file creation creates conditions to prepare the daily notification script immediately.
                self.__previous_jobs = {'Titles': [], "date_json_mod": str(datetime.now() - timedelta(days=1)), "new_job_detected": True}
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
    
    def set_current_jobs(self, child=False):
        """This is the setter method for self.__current_jobs.
        This method gets a webpage and scrapes it for jobs. It can either operate on tags with unique identifiers or the immediate child of a tag with a unique identifier.

        Args:
            child (bool, optional): Sets whether you're looking in the child of the identifiable tag for the job information. Defaults to False.

        Returns:
            List of strings: List of job titles currently available at the company.
        """
        try:
            self.__driver.get(self.__url)

            # When the target element is present, scrape and parse html.
            WebDriverWait(self.__driver, 10).until(
                EC.presence_of_element_located((self.__title_class_by_selector, self.__job_title_tag_attr_val))
            )
        
        except Exception as e:
            print(e)

        else:
            def scrape_job_titles():
                html = self.__driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # Locate job titles.
                # Hey, so... I've only actually tested this on 'class name'. I don't actually know yet whether the other cases work until I get around to finding a bunch of instances in which I need them to work.
                match self.__title_class_by_selector:
                    case 'id':
                        tags = soup.find_all(self.__job_title_tag, id=self.__job_title_tag_attr_val)    # This kwarg *might* work. Haven't tested it.
                    case 'name':
                        tags = soup.find_all(self.__job_title_tag, name=self.__job_title_tag_attr_val)    # This kwarg *might* work. Haven't tested it.
                    case 'xpath':
                        tags = soup.find_all(self.__job_title_tag, xpath=self.__job_title_tag_attr_val)    # This kwarg *might* work. Haven't tested it.
                    case 'link text':
                        pass    # I don't even know which kwarg to use here, and I won't until I have a good reason to figure it out.
                    case 'partial link text':
                        pass    # I don't even know which kwarg to use here, and I won't until I have a good reason to figure it out.
                    case 'tag name':
                        pass    # I don't even know which kwarg to use here, and I won't until I have a good reason to figure it out.
                    case 'class name':
                        tags = soup.find_all(self.__job_title_tag, class_=self.__job_title_tag_attr_val)
                    case 'css selector':
                        pass    # I don't even know which kwarg to use here, and I won't until I have a good reason to figure it out.
                
                if child == False:
                    for job_title_tag in tags:
                        if str(type(job_title_tag.string)) != "<class 'NoneType'>":    # If a tag with no text is targeted, it returns an element of this type. This is a specific fix for a page that reused the element containing the job title elsewhere in the page with a different structure where it didn't contain the job title. Obviously a unique identifier is picked for scraping, but this seems to be an edge case. The reused tag with the same identifier was related to job listings, but it was a redundant "highlighted jobs" section.
                            self.__current_jobs.append(job_title_tag.string.replace('\u200b', '').replace('\u2013', '-').strip())
                else:
                    # Pull the string from the child of each uniquely identifiable parent tag. Only works if there's only one child.
                    for parent_tag in tags:
                        if str(type(parent_tag.string)) != "<class 'NoneType'>":
                            self.__current_jobs.append(parent_tag.find().string.replace('\u200b', '').replace('\u2013', '-').strip())
            
            def click_button():
                try:
                    button = WebDriverWait(self.__driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f'//button[{self.__show_more_button_text}]'))
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

    def dump_current_jobs_json(self, new_job_detected):
        """This method saves the current job listings to a .json file for comparison to future job listings.

        Args:
            new_job_detected (bool): Used when building the daily notification during the first run of each day to determine whether jobs were detected the previous day.
        """
        json_formatted_data = {'Titles':self.__current_jobs, 'date_json_mod':datetime.now(), 'new_job_detected':new_job_detected}

        def write_json():
            with open(self.__company_data_filepath, 'w') as file:
                    json.dump(json_formatted_data, file, indent=4, default=str)    # default=str tells the .json file how to handle non-serializable type, such as datetime. Should be okay here since I know exactly what's getting stored every time.
                    file.close()

        try:
            with open(self.__company_data_filepath, 'r') as file:
                file.close()
        except FileNotFoundError:
            # The initial creation/writing to the .json has weird recursive effects in Termux. Writing to it twice fixes it... Windows functions as expected.
            for i in range(2):
                write_json()
        else:
            write_json()
    
    def send_notification(self, notif_type):
        """Build and send notifications about the status of job listings at the company.

        Args:
            notif_type (str): 'per_execution': Per-execution notification about finding a new job listing.
                              'daily': Daily summary notification sent regardless of findings.
                              'error_getting_current_jobs': Failure to retrieve current job listings.
        """
        # Choose content of the notification
        match notif_type:
            case 'per_execution':
                self.__notification_command = f'termux-notification --title "{self.__new_jobs_today_msg_title}" --content "Tap now to visit the {self.__company_name} careers page." --action "termux-open-url {self.__url}" --id big_employed-{self.__company_name} --image-path {self.__job_jpg_filepath} --button1 "Dismiss" --button1-action "termux-notification-remove big_employed-{self.__company_name}" '
            case 'daily':
                if self.__previous_jobs['new_job_detected'] == False:
                    self.__notification_command = f'termux-notification --title "{self.__no_jobs_yesterday_msg_title}" --content "Keep eating ramen noodles." --id big_unemployed-daily-{self.__company_name} --image-path {self.__no_job_jpg_filepath} --button1 "Dismiss" --button1-action "termux-notification-remove big_unemployed-daily-{self.__company_name}" '
                else:
                    self.__notification_command = f'termux-notification --title "{self.__new_jobs_yesterday_msg_title}" --content "Tap now to visit the {self.__company_name} careers page." --action "termux-open-url {self.__url}" --id big_employed-daily-{self.__company_name} --image-path {self.__job_jpg_filepath} --button1 "Dismiss" --button1-action "termux-notification-remove big_employed-daily-{self.__company_name}" '
            case 'error_getting_current_jobs':
                self.__notification_command = f'termux-notification --title "Failed to retrieve current listings" --content "Tap now to visit the {self.__company_name} careers page." --action "termux-open-url {self.__url}" --id failure-to-retrieve-jobs-{self.__company_name} --button1 "Dismiss" --button1-action "termux-notification-remove failure-to-retrieve-jobs-{self.__company_name}" '
            case 'error_getting_previous_jobs':
                self.__notification_command = f'termux-notification --title "Failed to load previous listings" --content "Check the {self.__company_name} .json file for existence and for potential errors." --action "termux-open-url {self.__url}" --id failure-to-load-jobs-{self.__company_name} --button1 "Dismiss" --button1-action "termux-notification-remove failure-to-load-jobs-{self.__company_name}" '
        
        # Send the notification
        if notif_type == 'daily':
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
                file.close()
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
        main() builds company objects, scrapes current jobs, compares to previous jobs, and reports the detection of new jobs.
            * Users receive one daily update notification:
                * If a new job was found yesterday, the daily notification informs the user.
                * If no new jobs were found, the daily notification informs the user of their continued unemployment.
            * In addition, when a new listing is detected, the user receives a per-execution notification on every subsequent run of the day to ensure visibility.
        
        desktop_scraper() is a version of main() that's been stripped down for Windows-64 systems. It is used to easily test which attributes work for scraping new commpany job pages.
            
        How to use:
        * To track new companies:
            * Check the company's robots.txt and respect their wishes.
            * Comment out the main() entry point and uncomment the desktop_scraper() entry point.
            * Follow the instructions in the desktop_scraper() docstring to test the scraper on new companies.
            * In main(), create and fill out a new company attributes list and then add that list's name to `companies`.
            * Re-comment the desktop_scraper() entry point and uncomment the main() entry point after testing.
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
        does_child_of_targeted_tag_contain_job_title_Boolean (sometimes job titles live inside indistinct tags that are children of uniquely targetable tags - is this the case, True or False? Only works when the tag with the job title has no siblings.),
        'name_of_attribute_used_for_job_title_tag_selection' (**NOTE**: THIS WILL FAIL IF YOU DON'T USE A VALID VALUE. NOT ALL OF THESE HAVE BEEN TESTED YET. The name of the attribute used to uniquely select job title tag. e.g. 'id', 'name', 'xpath', 'link text', 'partial link text', 'tag name', 'class name', 'css selector'),
        'unique_job_title_tag_attr_val' (a unique attribute for targeting job title tags),
        do_job_titles_load_by_individual_pages_Boolean (i.e. Is there a button like "show next" that loads one page at a time, only displaying some of the job titles (True), or is there a button like "show more" that, when clicked, displays all previously visible job titles **and** a new set of titles all at once after being clicked (False)?),
        'show_more/next_button_identifier' (Identifier for finding show more/next button by xpath. e.g. enter 'text()="Show more"' to get a final xpath of '//button[text()="Show more"]'. Another example would be 'contains(@aria-label, "next")'.)
    ]
    '''
    jagex = ['Jagex', 'https://apply.workable.com/jagex-limited/', 'h3', True, 'class name', 'styles--3TJHk', False, 'text()="Show more"']
    feathr = ['Feathr', 'https://jobs.ashbyhq.com/feathr', '', False, '', '', False,'']    # PRIMARY TARGET. I'M COMING FOR YOU; I ALWAYS WIN.
    # resilience = ['Resilience', 'https://resilience.wd1.myworkdayjobs.com/Resilience_Careers', 'a', False, 'class name', 'css-19uc56f', True, 'contains(@aria-label, "next")']    # Added simply to test a site that loads jobs by page, but kept because it's fun to keep tabs on old employers.
    admiral = ['Admiral', 'https://jobs.ashbyhq.com/admiral?embed=js', 'h3', False, 'class name', 'ashby-job-posting-brief-title', False, 'NonsenseGobbledygook']    # Unable to fill out more/next button info as it wasn't present when the copany was tested.
    infotech = ['Infotech', 'https://recruiting.ultipro.com/INF1010INFT/JobBoard/a1f626ce-9a88-4c30-86ee-6562ee8ea030/?q=&o=postedDateDesc', 'a', False, 'class name', 'opportunity-link', False, 'NonsenseGobbledygook']  # Unable to fill out more/next button info as it wasn't present when the copany was tested.
    mobiquity = ['Mobiquity', 'https://www.mobiquity.com/careers/americas/', '', False, '', '', False, '']    # Has a Gainesville office. I'd need to implement a way to filter by sibling elements before deciding to pull a job title because they have a lot of global positions. I can't guess how to filter for American jobs given there are none available right now. Worth checking on manually?
    byppo = ['Byppo', 'https://www.byppo.com/byppo-careers-page', '', False, '', '', False, '']    # Local, but has no listings available and so I don't know what to scrape for.
    opie = ['OPIE Software', 'https://www.opiesoftware.com/careers', '', False, '', '', False, '']    # Local company. No positions open, not sure how to scrape.
    golok = ['Golok', 'https://golokglobal.com/jobs/', 'h2', False, 'class name', 'awsm-job-post-title', False, 'NonsenseGobbledygook']    # Unable to fill out more/next button info as it wasn't present when the copany was tested.
    companies = [jagex, feathr, admiral, infotech, mobiquity, byppo, opie, golok]

    # Validate that no two companies 'n' have the same name in companies[n][0].
    company_names = [company[0] for company in companies]
    counter = Counter(company_names)
    duplicate_names = [i for i, j in counter.items() if j > 1]
    if duplicate_names:
        print('Error. Duplicate company name detected.')
        raise SystemExit

    # Begin execution
    this_execution = ThisExecution(
        project_version='1.0.0',
        fast_notifications=False
        )
    execution_logger = LogExecution(
        len(companies),
        this_execution.wd,
        this_execution.project_version
        )
    execution_logger.log_timestamp(start=True)
    new_job_detected = False

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
            this_execution.fast_notifications
            )
        
        # Compare current jobs to last execution's findings
        try:
            company_object.set_previous_jobs()
        except Exception:
            company_object.send_notification('error_getting_previous_jobs')
            continue

        try:
            company_object.set_current_jobs(child=company[3])
        except Exception:
            company_object.send_notification('error_getting_current_jobs')
            continue

        if company_object.current_jobs:    # Don't evaluate the newness of jobs if none exist
            for job in company_object.current_jobs:
                if job not in company_object.previous_jobs['Titles']:
                    new_job_detected = True
                    company_object.dump_current_jobs_json(new_job_detected)
                    break
            
        # Send notifications
        if datetime.strptime(company_object.previous_jobs['date_json_mod'], '%Y-%m-%d %H:%M:%S.%f').date() != date.today():
            # First execution of the day prepares the daily notification.
            if company_object.previous_jobs['new_job_detected'] == False:
                company_object.send_notification('daily')
            else:
                company_object.send_notification('daily')
                company_object.dump_current_jobs_json(new_job_detected)
        else:
            # Subsequent executions only notify is a job was found either on the current execution or earlier in the same day.
            if company_object.previous_jobs['new_job_detected'] == True:
                company_object.send_notification('per_execution')  # Index number is appended to --id attribute in termux-notification which generates a unique notification id per company so that notifications don't overwrite each other.

    # Log execution finish
    execution_logger.log_timestamp(start=False)

def desktop_scraper():
    """
        desktop_scraper() is a version of main() that's been stripped down for Windows-64 systems. It is used to easily test which attributes work for scraping new commpany job pages.

        How to use:
            * Check the company's robots.txt and respect their wishes.
            * Comment out the main() entry point and uncomment the desktop_scraper() entry point.
            * Excute the script from the parent project folder, otherwise the path will be built incorrectly.
            * The script needs to be executed from the command line; the VS Code debugger won't work.
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
        does_child_of_targeted_tag_contain_job_title_Boolean (sometimes job titles live inside indistinct tags that are children of uniquely targetable tags - is this the case, True or False? Only works when the tag with the job title has no siblings.),
        'name_of_attribute_used_for_job_title_tag_selection' (**NOTE**: THIS WILL FAIL IF YOU DON'T USE A VALID VALUE. NOT ALL OF THESE HAVE BEEN TESTED YET. The name of the attribute used to uniquely select job title tag. e.g. 'id', 'name', 'xpath', 'link text', 'partial link text', 'tag name', 'class name', 'css selector'),
        'unique_job_title_tag_attr_val' (a unique attribute for targeting job title tags),
        do_job_titles_load_by_individual_pages_Boolean (i.e. Is there a button like "show next" that loads one page at a time, only displaying some of the job titles (True), or is there a button like "show more" that, when clicked, displays all previously visible job titles **and** a new set of titles all at once after being clicked (False)?),
        'show_more/next_button_identifier' (Identifier for finding show more/next button by xpath. e.g. enter 'text()="Show more"' to get a final xpath of '//button[text()="Show more"]'. Another example would be 'contains(@aria-label, "next")'.
    ]
    '''
    new_company = ['Infotech', 'https://recruiting.ultipro.com/INF1010INFT/JobBoard/a1f626ce-9a88-4c30-86ee-6562ee8ea030/?q=&o=postedDateDesc', 'a', False, 'class name', 'opportunity-link', False, 'NonsenseGobbledygook']
    companies = [new_company]

    # Begin execution
    this_execution = ThisExecution()

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
            this_execution.fast_notifications
            )

        try:
            company_object.set_current_jobs(child=company[3])
        except Exception:
            print('Error retrieving current jobs.')
        print(company_object.current_jobs)       

if __name__ == '__main__':
    main()
    #desktop_scraper()    # Used to test the web-scraper in isolation on Windows when trying to scrape new companies.

"""
Notes for future work:
* I've accounted for this in the README, but will leave this section for future notes while working on the script.
"""