import logging
from file_management import clean_up_session_files, delete_session_files, update_drive_directory
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from file_management import clean_up_session_files, delete_session_files, update_drive_directory, clean_up_docs_files, remove_file_safely, is_file_valid, authorize_drive, view_in_drive_folder


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
# update_drive_directory(drive, 'docs' ,team_drive_id)

# scraper_service.login(username, password)

# scraper_service.scrape(username)

# scraper_service.reset(username)




team_drive_id = '0AFReXfsUal4rUk9PVA'

directory = view_in_drive_folder(drive, team_drive_id, team_drive_id)
print(directory)