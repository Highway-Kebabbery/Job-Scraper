#!/usr/bin/env python

"""Loads a company's provided careers page and uses the provided tag and attribute identifier to scrape job listings.
    Careers are compared against the last scrape to determine if a change occurred and a notification is sent to the host's phone.
"""

import os
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CompanyJobsFinder():
    """A class for finding and storing job listings available at a company."""

    __driver = None
    __company_name = ''
    __url = ''
    __target_tag = ''
    __target_attribute_value = ''
    __current_jobs = []
    __previous_jobs = None

    def __init__(self, company_name, url, target_tag, target_attribute_value):
        self.__company_name = company_name
        self.__url = url
        self.__target_tag = target_tag
        self.__target_attribute_value = target_attribute_value
        self.set_firefox_driver()
    
    def set_firefox_driver(self, mobile=True):
        """Set up the web driver

        Args:
            mobile (bool, optional): I set the script/project up to run both on Win64 (for basic configuration) and on Linux
            because the script is run through Termux on Android, which provides a Linux-based environment. When troubleshooting
            on Win64, don't forget to add the <mobile=False> argument when called in __init__. Defaults to True.
        """

        if mobile == False:
            # driver is in environment variables on Android and needs not be called.
            gecko_driver_path = './Drivers/win64/geckodriver.exe'
        service = FirefoxService(executable_path=gecko_driver_path)
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        if mobile == True:
            self.__driver = webdriver.Firefox(options=options)
        else:
            self.__driver = webdriver.Firefox(service=service, options=options)

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
        if os.path.exists('./Data/' + str(self.__company_name) + '.json'):
            with open('./Data/' + str(self.__company_name) + '.json', 'r') as file:
                self.__previous_jobs = json.load(file)
                file.close()

    @property
    def current_jobs(self):
        """Getter for self.__current_jobs

        Returns:
            List: Jobs currently posted on company website.
        """
        return self.__current_jobs
    
    def set_current_jobs_by_class(self, child=False):
        """This method gets a webpage and scrapes it for jobs. It can either operate on
        tags with unique identifiers, or the immediate child of a tag with a unique identifier.

        Args:
            child (bool, optional): Sets whether you're looking in the child of the
            identifiable tag for the job information. Defaults to False.

        Returns:
            list: This is the setter method for self.__current_jobs.
        """
        
        self.__driver.get(self.__url)

        # Wait until target element is present to ensure the page has fully loaded
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
                self.__current_jobs.append({"Title: ": target_tag.string})
        else:
            # Pull the string from the child of each uniquely identifiable parent tag.
            # Only works if there's only one child.
            for parent_tag in tags:
                self.__current_jobs.append({"Title: ": parent_tag.find().string})

        self.__driver.quit()

    def set_current_jobs_json(self):
        """This method saves the current job listings to a .json file for comparison to the old job listings.

        Args:
            company_name (string): Used to generate filename.
        """
        with open('./Data/' + str(self.__company_name) + '.json', 'w') as file:
            json.dump(self.__current_jobs, file, indent=4)
            file.close()

class SendNotifications(CompanyJobsFinder):
    """A class for organizing notificaiton content and schedules"""

    __company_name = ''
    __url = ''
    __new_listings_msg_title = f'Job listings updated for {__company_name}!'
    __no_listings_msg_title = f'No new jobs at {__company_name}.'


    def __init__(self, parent_instance):
        self.__company_name = parent_instance.company_name
        self.__url = parent_instance.url

    def send_notification(self, update_detected):
        cd = str(os.system('pwd'))
        if cd[-1] == "/":
            cd = cd[:-1]

        if update_detected == False:
            os.system(f'termux-notification --title {self.__no_listings_msg_title} --content "Keep eating ramen noodles." --id "big_unemployed" --image-path "{cd}/Media/noJob.jpg" ')
        else:
            os.system(f'termux-notification --title {self.__new_listings_msg_title} --content "Tap now to visit the {self.__company_name} careers page." --id "big_employed" --image-path "{cd}/Media/job.jpg" ')

def main():
    # Future idea when tracking 2+ companies. Make a dictionary containing initialization variables (plus mobile and child flag settings).
    # One dictionary per company, then I can make a list of companies and loop through them to generalize the code below. Everything including instantiation can be generalized.

    jagex = CompanyJobsFinder('Jagex', 'https://apply.workable.com/jagex-limited/', 'h3', 'styles--3TJHk')
    jagex.set_previous_jobs()
    jagex.set_current_jobs_by_class(child=True)
    jagex_notification = SendNotifications(jagex)

    # See notes 
    if jagex.previous_jobs == jagex.current_jobs:
        update_detected = False
        print(f'No new jobs at {jagex.company_name}Keep eating ramen noodles.') # Diagnostic print line. Comment out for production.
    else:
        update_detected = True
        jagex.set_current_jobs_json()
        print(f'Job listings updated for {jagex.company_name}! Tap now to view listings.')  # Diagnostic print line. Comment out for production.
    jagex_notification.send_notification(update_detected=update_detected)

if __name__ == '__main__':
    main()


"""
    Notes on notifications:
    * I need to figure out how to make actions happen when tapping notification.
    * Daily notification at set time either stating nothing was found or something was found for each company
    * Only send notifications on each run if a change was detected
    * Send daily notification of jobs that contain certain keywords
    * configure notification class to accept scrape/notification times for each job
"""




"""
    Notes for future work:
    * Program currently only checks whether the listings changed. This will register removals as well as new listings. Find a way to notate new listings.
    * I can probably do something like check to see if each current job is in the past jobs, and if each past job is in the current jobs.
        * If current job not in pastlistings, BOOM new listing, and I have its name and can store in a variable for use. If past job not in current listings... who cares. Maybe don't check for that after all.
    * I don't filter for keywords. This is fine for now as I'm targeting smaller companies with fewer listing updates, but for larger companies I'd want to filter new jobs by keyword.
    * I also only check for updates. I could feasibly use this class to simply check for jobs with certain keywords. For example: scrape company with many listings for jobs, then monitor over time for changes.
    * I'm going to need to handle instances where there are multiple pages of jobs. Another issue for when I target larger companies. Selenium should make it easy to handle.
"""