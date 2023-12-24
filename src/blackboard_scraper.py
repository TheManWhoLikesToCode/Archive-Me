import os
import re
import requests
import ray
import logging
import mimetypes
import zipfile
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_into_blackboard(driver, username, password):
    driver.set_page_load_timeout(3)

    try:
        driver.get("https://blackboard.kettering.edu/")

        if check_logged_in(driver, wait_time=1):
            return driver  # User is already logged in

        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#loginForm")))

        username_field = driver.find_element(By.CSS_SELECTOR, "#inputUserID")
        password_field = driver.find_element(By.CSS_SELECTOR, "#inputPassword")
        login_button = driver.find_element(
            By.CSS_SELECTOR, "#loginForm > button")

        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()

        WebDriverWait(driver, 3).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#loginForm")))

        try:
            cookies_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#agree_button")))
            cookies_button.click()
        except TimeoutException:
            pass  # Cookie button not found or not clickable

    except TimeoutException:
        error_message_element = driver.find_element(
            By.CSS_SELECTOR, "#loginForm > div:nth-child(2) > div")
        error_message = error_message_element.text.strip()
        if error_message:
            return f"Login failed: {error_message}"
        else:
            return "Login failed: Timeout reached."

    except NoSuchElementException:
        error_message_element = driver.find_element(
            By.CSS_SELECTOR, "#loginForm > div:nth-child(2) > div")
        error_message = error_message_element.text.strip()
        if error_message:
            return f"Login failed: {error_message}"
        else:
            return "Login failed, but no specific error message found."

    return driver  # Return the logged-in driver


def check_logged_in(driver, wait_time):
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#globalNavPageNavArea > table")))
        return True
    except TimeoutException:
        return False

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


def scrape_grades_from_blackboard(driver):
    """
    Args:
        username (str): The username for the Blackboard account
        password (str): The password for the Blackboard account
    Returns:
        None
    Notes: 
        passes all_grades to generate html
    """

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


@ray.remote
def download_and_save_file(course_name, assignment_name, url, cookies):
    os.makedirs(course_name, exist_ok=True)

    with requests.Session() as s:
        s.cookies.update(cookies)
        response = s.get(url)

    content_type = response.headers.get('Content-Type')
    guessed_extension = mimetypes.guess_extension(content_type)

    # Extract current extension from assignment_name
    name, current_extension = os.path.splitext(assignment_name)

    # Determine if the current extension is appropriate
    if current_extension:
        mime_of_current_extension = mimetypes.guess_type(assignment_name)[0]
        if mime_of_current_extension == content_type:
            extension = current_extension  # Current extension is correct
        else:
            # Replace with guessed or keep current
            extension = guessed_extension or current_extension
    else:
        # Check for HTML content before defaulting to .bin
        if 'html' in content_type or b'<html' in response.content or b'<!DOCTYPE HTML' in response.content or b'<html lang="en-US">' in response.content:
            extension = '.html'
        else:
            # Default to .bin if no extension is guessed
            extension = guessed_extension or '.bin'

    # Adjust file name
    file_path = os.path.join(course_name, name + extension)

    with open(file_path, "wb") as f:
        f.write(response.content)


def get_cookies(driver):
    return {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}


def scrape_content_from_blackboard(driver):
    # Assuming this function logs into Blackboard
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    try:
        div_4_1 = soup.find("div", id="div_4_1")
        courses = div_4_1.find_all("ul")[0]
    except Exception as e:
        print(e)
        return

    hrefs = {course.text.strip(): course.find("a")["href"].strip(
    ) for course in courses.find_all("li") if course.find("a")["href"]}

    cookies = get_cookies(driver)
    download_tasks = []

    for course, href in hrefs.items():
        course_name = re.sub(r'[\\/:*?"<>|]', '', course.strip("\n"))
        full_url = "https://kettering.blackboard.com" + href
        driver.get(full_url)
        driver.implicitly_wait(10)  # Consider explicit waits here
        soup = BeautifulSoup(driver.page_source, "html.parser")
        menu_puller_a = driver.find_element(By.ID, "menuPuller")
        menu_puller_a.click()
        driver.implicitly_wait(10)
        menuWrap = soup.find("div", id="menuWrap")
        course_menu = menuWrap.find("ul", class_="courseMenu")

        for li in course_menu.find_all("li"):
            try:
                href = li.find("a")["href"]
                if href[0] != "/":
                    continue
                full_url = "https://kettering.blackboard.com" + href
                driver.get(full_url)
                driver.implicitly_wait(10)
                current_page = BeautifulSoup(driver.page_source, "html.parser")
                content_listContainer = current_page.find(
                    'ul', {'id': 'content_listContainer', 'class': 'contentListPlain'})

                if content_listContainer:
                    for li in content_listContainer.find_all('li'):
                        assignment_name = re.sub(
                            r'[\\/:*?"<>|]', '_', li.text.strip().split("\n")[0] or "Untitled")
                        a = li.select_one('a')
                        if a and a['href'][0] != "h":
                            full_url = "https://kettering.blackboard.com" + \
                                a['href']
                            download_tasks.append(download_and_save_file.remote(
                                course_name, assignment_name, full_url, cookies))
            except Exception as e:
                continue

    # Wait for all downloads to complete
    ray.get(download_tasks)


def download_and_zip_content(driver, username):
    """
    Scrape the content from Blackboard and zip it.

    Args:
        driver: Selenium WebDriver instance.
        username (str): The username for the Blackboard account.
        password (str): The password for the Blackboard account.

    Returns:
        str: The path of the created zip file.
    """

    # Scrape the content from Blackboard
    scrape_content_from_blackboard(
        driver)

    zip_file_path = username + '_downloaded_content.zip'
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk('.'):
            for file in files:
                # Add other file types if needed
                if file.endswith('.pdf') or file.endswith('.docx'):
                    zipf.write(os.path.join(root, file))

    # Return the path of the zip file
    return zip_file_path
