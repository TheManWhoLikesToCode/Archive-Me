import os
import re
import shutil
import zipfile
import mimetypes
import requests
import ray
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_argument("--disable-images")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# * Logs a user into the Blackboard website using Selenium WebDriver.


def log_into_blackboard(driver, username, password):
    driver.set_page_load_timeout(10)

    try:
        driver.get("https://blackboard.kettering.edu/")

        # Wait for redirect
        WebDriverWait(driver, 10).until(
            EC.url_changes("https://blackboard.kettering.edu/"))

        # Find the login form elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm")))
        username_field = driver.find_element(By.ID, "inputUserID")
        password_field = driver.find_element(By.ID, "inputPassword")
        login_button = driver.find_element(By.ID, "sign-button")

        # Enter credentials and submit
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()

        # Handle cookie button if present
        try:
            cookies_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "agree_button")))
            cookies_button.click()
        except TimeoutException:
            pass  # Cookie button not found or not clickable

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error during login: {e}")


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


def scrape_grades_from_blackboard(driver, username, password):
    """
    Args:
        username (str): The username for the Blackboard account
        password (str): The password for the Blackboard account
    Returns:
        None
    Notes: 
        passes all_grades to generate html
    """

    # login to blackboard
    log_into_blackboard(driver, username, password)

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


ray.init()


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
        if 'html' in content_type or b'<html' in response.content:
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


def scrape_content_from_blackboard(driver, blackboard_username, blackboard_password):
    # Assuming this function logs into Blackboard
    log_into_blackboard(driver, blackboard_username, blackboard_password)
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


def download_and_zip_content(driver, username, password):
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
        driver, username, password)

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
    excluded_folders = ['src', 'docs', 'support', '.vscode', '.git']

    for item in os.listdir():
        if os.path.isdir(item) and item not in excluded_folders:
            source_path = item
            dest_path = os.path.join('docs', item)

            if not os.path.exists(dest_path):
                shutil.move(source_path, dest_path)
            else:
                for sub_item in os.listdir(source_path):
                    source_sub_item = os.path.join(source_path, sub_item)
                    dest_sub_item = os.path.join(dest_path, sub_item)

                    if os.path.isdir(source_sub_item):
                        if not os.path.exists(dest_sub_item):
                            shutil.move(source_sub_item, dest_sub_item)
                        else:
                            # Remove existing directory before moving
                            shutil.rmtree(dest_sub_item)
                            shutil.move(source_sub_item, dest_sub_item)
                    elif os.path.isfile(source_sub_item) and not os.path.exists(dest_sub_item):
                        shutil.move(source_sub_item, dest_sub_item)

                if not os.listdir(source_path):  # Check if directory is now empty
                    shutil.rmtree(source_path)  # Safe to remove

            print(f"Processed {item}")

    print("Folders merged into 'docs' successfully.")

    if os.path.exists('downloaded_content.zip'):
        os.remove('downloaded_content.zip')

    print("Clean-up completed.")



# Usage Example


driver = webdriver.Chrome(options=chrome_options)

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
