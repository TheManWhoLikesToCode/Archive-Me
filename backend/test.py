import logging
import ray
from backend.blackboard_scraper_S import (
    download_and_zip_content,
    log_into_blackboard,
    scrape_content_from_blackboard,
    scrape_grades_from_blackboard,
)
from config import chrome_options
from file_management import clean_up_session_files, delete_session_files, update_drive_directory
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class ScraperService:
    def __init__(self):
        self.drivers = {}
        logging.info("ScraperService initialized")

    def initialize_driver(self, username):
        logging.info(f"Initializing driver for {username}")
        if username not in self.drivers:
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(
                    service=service, options=chrome_options)
                self.drivers[username] = driver
            except Exception as e:
                logging.error(
                    f"Error initializing WebDriver for {username}: {e}")
                raise
        return self.drivers[username]

    def login(self, username, password):
        logging.info(f"Logging in {username}")
        try:
            driver = self.initialize_driver(username)
            return log_into_blackboard(driver, username, password)
        except Exception as e:
            logging.error(f"Error during login for {username}: {e}")
            self.reset(username)
            raise

    def scrape(self, username):
        logging.info(f"Scraping data for {username}")
        driver = self.drivers.get(username)
        if not driver:
            raise Exception("User not logged in or session expired")

        try:
            return download_and_zip_content(driver, username)
        except Exception as e:
            logging.error(f"Error during scraping for {username}: {e}")
            raise
        finally:
            self.reset(username)

    def reset(self, username):
        logging.info(f"Resetting driver for {username}")
        driver = self.drivers.pop(username, None)
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logging.error(f"Error closing WebDriver for {username}: {e}")


scraper_service = ScraperService()

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


# ray.init()
# driver = webdriver.Chrome(options=chrome_options)

# * Log Into Blackboard
# log_into_blackboard(driver, username, password)

# * Get Instructors
# instructors = get_instructors(driver)

# * Function To Download All Files From Blackboard
# Time = 45 Seconds
# scrape_content_from_blackboard(driver)

# * Function To Get Grades From Blackboard
# scrape_grades_from_blackboard(driver, username, password)

# * Funct to Download and zip content
# download_and_zip_content(driver, username, password)

# * Clean up files
# Pre - 204.7 MB
# 5 folders - 140.1 MB
# clean_up_session_files(False)

# * Delete session files
# delete_session_files()

# * Close the WebDriver
# driver.quit()

# * Update Drive
update_drive_directory(drive, 'docs' ,team_drive_id)

# scraper_service.login(username, password)

# scraper_service.scrape(username)

# scraper_service.reset(username)

