from selenium import webdriver
from blackboard_scraper import log_into_blackboard, scrape_content_from_blackboard, scrape_grades_from_blackboard, download_and_zip_content, clean_up_files
from config import chrome_options
from file_management import clean_up_files
import ray

# ray.init()
# driver = webdriver.Chrome(options=chrome_options)

# * Log Into Blackboard
# driver = log_into_blackboard(driver, username, password)

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
# clean_up_files()

# Close the WebDriver
# driver.quit()
