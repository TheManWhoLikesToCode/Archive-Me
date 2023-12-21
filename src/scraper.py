# Import the necessary modules
import shutil
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import zipfile
import os
import re


# * Logs a user into the Blackboard website using Selenium WebDriver.
def log_into_blackboard(driver, username, password):
    """
    Arguments:
        driver (webdriver.Firefox, webdriver.Chrome, ...): Selenium WebDriver instance.
        username (str): User's username.
        password (str): User's password.
    """

    # Wait for up to 10 seconds for elements to become available
    driver.implicitly_wait(10)

    # Go to the login page
    driver.get("https://blackboard.kettering.edu/")

    # Wait for the redirect to occur
    while driver.current_url == "https://blackboard.kettering.edu/":
        pass

    # Find the login form
    login_form = driver.find_element(By.ID, "loginForm")

    # Find the username, password, and login button fields
    username_field = login_form.find_element(By.ID, "inputUserID")
    password_field = login_form.find_element(By.ID, "inputPassword")
    login_button = login_form.find_element(By.ID, "sign-button")

    # Enter the username and password
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Click the login button using JavaScript
    driver.execute_script("arguments[0].click();", login_button)

    # Wait for the redirect to occur
    cookies_button = driver.find_element(By.ID, "agree_button")
    cookies_button.click()


# * Extracts the links to the grades pages of the user's courses from the home page of the Blackboard website.
def get_grades_page_links(driver):
    """
    Arguments:
        driver (webdriver.Firefox, webdriver.Chrome, ...): Selenium WebDriver instance.
    Returns:
        dict: A dictionary mapping course names to their corresponding grades page links.
    """
    # Get the HTML source code of the page
    html = driver.page_source

    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find div element with id div_19_1
    div_element = soup.find("div", id="div_19_1")

    # Get the table with the class name bMedium reportcard
    grades_table = div_element.find("table", class_="bMedium reportcard")

    # Get the rows of the table
    rows = grades_table.find_all("tr")

    # remove the first row
    rows.pop(0)

    # Make a dictionary to store the grades page links
    grades_page_links = {}

    # Iterate over the rows and get the href attribute of the anchor element
    for row in rows:
        # look under td for name of course and grade link
        td_elements = row.find_all("td")

        # For element one get the text
        course_name = td_elements[0].text

        # For element two get the href attribute
        href = td_elements[1].a["href"]

        # add it to the dictionary
        grades_page_links[course_name] = href

    # Return the dictionary
    return grades_page_links


# * Extracts the grades for all the assignments in a course from the course grades page on the Blackboard website.
def extract_grades(soup):
    """
    Arguments:
        soup (BeautifulSoup object): BeautifulSoup object of the course grades page.
    Returns:
        list: A list of lists containing the assignment names and their corresponding grades.
    """
    # Create a matrix to store the assignment names and grades
    grades = []

    # Find the div element containing the grades
    div_element = soup.find(
        'div', {'class': 'container clearfix', 'id': 'containerdiv'})

    # Find the grades wrapper element
    grades_wrapper = div_element.find(id='grades_wrapper')

    # Find every div element with the role row
    row_elements = grades_wrapper.find_all('div', {'role': 'row'})

    # Iterate over the row elements
    for row in row_elements:
        try:
            # Find the class cell gradable
            class_cell = row.find('div', {'class': 'cell gradable'})
            # Find all elements under the class cell gradable
            assignment_elements = class_cell.find_all()
            # Get the text from the first element
            assignment_name = assignment_elements[0].text

            # Find the cell grade div
            grade_cell = row.find('div', {'class': 'cell grade'})
            # Find the class grade in the cell grade div
            grade_element = grade_cell.find('span', {'class': 'grade'})
            # Get the text of the grade span
            grade_text = grade_element.text

            # Append the assignment name and grade to the grades list
            grades.append([assignment_name, grade_text])
        except:
            pass

    return grades

# * Generates an HTML file displaying the grades.


def generate_html(grades):
    """
    Args:
        grades (dict): A dictionary where each key is the name of a course, 
        and each value is a list of grades for that course.

    Returns:
        None

    Note: 
        Creates a html file
    """
    # Create an empty string to store the HTML code
    html_code = ""

    # Add the HTML header and title
    html_code += "<html>\n"
    html_code += "<head>\n"
    html_code += "<title>Grades</title>\n"
    html_code += "</head>\n"

    # Add the body of the HTML page
    html_code += "<body>\n"

    # Add a heading
    html_code += "<h1>Grades</h1>\n"

    # Add a table to display the grades
    html_code += "<table>\n"

    # Add a list item for each course
    for course, grades_list in grades.items():
        # Make the course a header
        html_code += "<h3>{}</h3>\n".format(course)

        # Add an inner unordered list to display the grades for the course
        html_code += "<ul>\n"

        # Add a list item for each grade
        for grade in grades_list:
            # Remove the brackets and single quotes from the grade
            grade = str(grade).strip("[]")
            html_code += "<li>{}</li>\n".format(grade)

        # Close the inner unordered list
        html_code += "</ul>\n"

        # Close the list item
        html_code += "</li>\n"

    # Close the outer unordered list
    html_code += "</ul>\n"

    # Close the body and HTML tags
    html_code += "</body>\n"
    html_code += "</html>\n"

    # Save the HTML code to a file
    with open("grades.html", "w") as f:
        f.write(html_code)

# * This function scrapes the grades from Blackboard for a given username and password.


def scrape_grades_from_blackboard(driver, blackboard_username, blackboard_password):
    """
    Args:
        blackboard_username (str): The username for the Blackboard account
        blackboard_password (str): The password for the Blackboard account
    Returns:
        None
    Notes: 
        passes all_grades to generate html
    """

    # login to blackboard
    log_into_blackboard(driver, blackboard_username, blackboard_password)

    # Go to the grades page and get a list of course hrefs
    course_hrefs = get_grades_page_links(driver)

    # Create a dictionary to store the grades
    all_grades = {}

    # For each href in the dictionary
    for href in course_hrefs.values():
        # Append the href to the base url
        full_url = "https://kettering.blackboard.com" + href
        # Scrape the href
        driver.get(full_url)
        # Wait for the page to load
        driver.implicitly_wait(10)
        # Get the HTML source code of the page
        html = driver.page_source
        # Parse the HTML code using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        # Get the div id courseMenuPalette_paletteTitleHeading
        course_name = soup.find(
            "div", id="courseMenuPalette_paletteTitleHeading")
        # Get the text from the course name
        course_name = course_name.text
        # Create a dictionary to store the grades
        grades = {}
        # call the scrape grades function
        grades = extract_grades(soup)

        # Add to the all_grades dictionary
        all_grades[course_name] = grades

    # Generate the HTML file
    generate_html(all_grades)
    # Close the browser
    driver.close()

# * This function scrapes the content from the blackboard website by logging in to the blackboard website, accessing the courses and content,
# * and extracting the course and assignment names and URLs.


def scrape_content_from_blackboard(driver, blackboard_username, blackboard_password):
    """
    Arguments:
    blackboard_username - str: The username for the blackboard account.
    blackboard_password - str: The password for the blackboard account.

    Returns: None
    """

    # login to blackboard
    log_into_blackboard(driver, blackboard_username, blackboard_password)
    # Get the html source code
    html = driver.page_source
    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    content_links = {}

    # Add try-except block
    try:
        # Get the div id div_4_1
        div_4_1 = soup.find("div", id="div_4_1")
        # Get the ul element
        courses = div_4_1.find_all("ul")[0]

    except Exception as e:
        print(e)
        return

    # Create a dictionary to store the hrefs
    hrefs = {}
    # for each li element in the courses get the href
    for course in courses.find_all("li"):
        # Get the href
        href = course.find("a")["href"]
        # If the href is empty, skip it
        if href == "":
            continue
        # Remove empty spaces from the href
        href = href.strip()
        # Add the href to the dictionary
        hrefs[course.text] = href

    # Visit each course
    for course, href in hrefs.items():
        # Course name = course minus \n
        course_name = course.strip("\n")
        course_name = re.sub(r'[\\/:*?"<>|]', '', course_name)
        # Append the href to the base url
        full_url = "https://kettering.blackboard.com" + href
        # Scrape the href
        driver.get(full_url)
        # Wait for the page to load
        driver.implicitly_wait(10)
        # Get the HTML source code of the page
        html = driver.page_source
        # Parse the HTML code using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        # Find the a element with id "menuPuller"
        menu_puller_a = driver.find_element(By.ID, "menuPuller")
        # Wait for the page to load
        driver.implicitly_wait(10)
        # Click the div element
        menu_puller_a.click()
        # Get the div id courseMenuPalette_contents
        menuWrap = soup.find("div", id="menuWrap")
        # get the class courseMenu
        course_menu = menuWrap.find("ul", class_="courseMenu")

        # for each li element in the course menu
        for li in course_menu.find_all("li"):
            # Try to get the href if it doesn't exist, skip it
            try:
                # Get the href
                href = li.find("a")["href"]
            except:
                continue

            # if href isn't a relative url, skip it
            if href[0] != "/":
                continue
            # Append the href to the base url
            full_url = "https://kettering.blackboard.com" + href
            # Scrape the href
            driver.get(full_url)
            # Wait for the page to load
            driver.implicitly_wait(10)
            # Soup ts
            current_page = BeautifulSoup(driver.page_source, "html.parser")

            # Find the all the ul elements
            content_listContainer = current_page.find(
                'ul', {'id': 'content_listContainer', 'class': 'contentListPlain'})

            # If none, skip it
            if content_listContainer is None:
                continue

            # Find all of the li elements
            content_listContainer = content_listContainer.find_all('li')
            # For each li element look for the ul class attachments clearfix
            for li in content_listContainer:
                # Assigment Name
                assignment_name = li.text
                # Remove \n
                assignment_name = assignment_name.strip("\n")
                # Remove everything after the first \n
                assignment_name = assignment_name.split("\n")[0]
                # Remove all special characters
                assignment_name = re.sub(r'[\\/:*?"<>|]', '_', assignment_name)

                # If the assignment name is give it a default name
                if assignment_name == "":
                    assignment_name = "Untitled"

                # Select the a element
                a = li.select_one('a')
                # if a is None, skip it
                if a is None:
                    continue
                # Get the href attribute
                href = a['href']
                # If the href is a full url, skip it
                if href[0] == "h":
                    continue
                # Append the href to the base url
                full_url = "https://kettering.blackboard.com" + href
                # Save the full url
                driver.get(full_url)
                # Wait for the page to load
                driver.implicitly_wait(10)
                # get the website url
                url = driver.current_url
                # store this in content_links
                content_links[assignment_name] = url

            # Iterate through the content_links and download and save the files
            for assignment_name, url in content_links.items():
                # Check if the directory exists
                if not os.path.exists(course_name):
                    # Create the directory
                    os.makedirs(course_name)
                # Download the file
                response = requests.get(url)
                # Save the file
                with open(course_name + "/" + assignment_name, "wb") as f:
                    f.write(response.content)
                # Clear the content_links
            content_links.clear()


def download_and_zip_content(driver, blackboard_username, blackboard_password):
    """
    Scrape the content from Blackboard and zip it.

    Args:
        driver: Selenium WebDriver instance.
        blackboard_username (str): The username for the Blackboard account.
        blackboard_password (str): The password for the Blackboard account.

    Returns:
        str: The path of the created zip file.
    """

    # Scrape the content from Blackboard
    scrape_content_from_blackboard(
        driver, blackboard_username, blackboard_password)

    zip_file_path = username + '_downloaded_content.zip'
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk('.'):
            for file in files:
                # Add other file types if needed
                if file.endswith('.pdf') or file.endswith('.docx'):
                    zipf.write(os.path.join(root, file))

    # Return the path of the zip file
    return zip_file_path


def clean_up_files():
    """
    Deletes the directories and files created during the scraping process, 
    avoiding duplicates in the 'docs' folder.
    """
    # Define the folders to exclude from moving
    excluded_folders = ['src', 'docs', 'support']

    # Iterate through each item in the current directory
    for item in os.listdir():
        # Check if the item is a directory and not in the excluded list
        if os.path.isdir(item) and item not in excluded_folders:
            # Construct the new path inside the 'docs' folder
            new_path = os.path.join('docs', item)

            # Check for duplicates
            if not os.path.exists(new_path):
                # Move the folder to the new path
                shutil.move(item, new_path)
            else:
                print(f"Duplicate found, not moving {item}")

    print("Folders moved to 'docs' successfully.")

    # Delete the zip file if it exists
    if os.path.exists('downloaded_content.zip'):
        os.remove('downloaded_content.zip')

    print("Clean-up completed.")


# Usage Example
username = "free8864"
password = "#CFi^F6TTwot2j"

driver = webdriver.Chrome()

# * Log Into Blackboard
# log_into_blackboard(driver, username, password)

# * Function To Download All Files From Blackboard
# scrape_content_from_blackboard(driver, username, password)

# * Function To Get Grades From Blackboard
# scrape_grades_from_blackboard(driver, username, password)

# * Funct to Download and zip content
# download_and_zip_content(driver, username, password)

# * Clean up files
# clean_up_files()

# Close the WebDriver
driver.quit()
