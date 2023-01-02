# Import the necessary modules
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options


def log_into_blackboard(driver, username, password):
    # Wait for up to 10 seconds for elements to become available
    driver.implicitly_wait(10)

    # Go to the login page
    driver.get("https://blackboard.kettering.edu/")

    # Wait for the redirect to occur
    while driver.current_url == "https://blackboard.kettering.edu/":
        pass

    # Find the username field
    login_form = driver.find_element(By.ID, "loginForm")

    # Find the username and password fields
    username_field = login_form.find_element(By.ID, "inputUserID")

    password_field = login_form.find_element(By.ID, "inputPassword")

    # Enter the username and password
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Find the login button and click it
    login_button = login_form.find_element(By.ID, "sign-button")
    # Click the login button
    login_button.click()

    # Wait for the redirect to occur
    cookies_button = driver.find_element(By.ID, "agree_button")
    cookies_button.click()


def get_grades_page_links(driver):
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



def extract_grades(soup):
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



def generate_html(grades):
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


def scrape_grades_from_blackboard(blackboard_username, blackboard_password):
    # Create a new Chrome session
    driver = webdriver.Chrome()
    #login to blackboard
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


def scrape_content_from_blackboard(blackboard_username, blackboard_password):
    # Create a new Chrome session
    driver = webdriver.Chrome()
    #login to blackboard
    log_into_blackboard(driver, blackboard_username, blackboard_password)
    # Get the html source code
    html = driver.page_source
    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    # Get the div id div_4_1
    div_4_1 = soup.find("div", id="div_4_1")
    # select the second div element
    courses_where_you_are_a_student = div_4_1.find_all("div")[1]
    # Select the first ul element
    courses = courses_where_you_are_a_student.find_all("ul")[0]
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
            # Get the href
            href = li.find("a")["href"]
            # Append the href to the base url
            full_url = "https://kettering.blackboard.com" + href
            # Scrape the href
            driver.get(full_url)
            # Wait for the page to load
            driver.implicitly_wait(10)

        try:
            # Find the div content_listContainer
            content_listContainer = soup.find("div", class_="content_listContainer")
            # For each of the listed items in the content_listContainer
            for item in content_listContainer.find_all("li"):
                # Get the href
                href = item.find("a")["href"]
                # Append the href to the base url
                full_url = "https://kettering.blackboard.com" + href
                # Scrape the href
            driver.get(full_url)
        except Exception as e:
            # If there is an exception, print the error message
            print(e)

        


        

    print("Pause")

    # Login to the blackboard
