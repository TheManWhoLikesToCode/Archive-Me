# Import the necessary modules
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options


def login(driver, username, password):
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


def get_course_href(driver):

    # Get the HTML source code of the page
    html = driver.page_source

    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find div id div_19_1
    div_element = soup.find("div", id="div_19_1")

    # Get the table with the class name bMedium reportcard
    grade_table = div_element.find("table", class_="bMedium reportcard")

    # Get the rows of the table
    grade_rows = grade_table.find_all("tr")

    # remove the first row
    grade_rows.pop(0)

    # Make a dictionary to store the grades
    course_href = {}

    # Iterate over the rows and get the href attribute of the anchor element
    for row in grade_rows:
        # look under td for name of course and grade link
        td_element = row.find_all("td")

        # For element one get the text
        td_element[0] = td_element[0].text

        # For element two get the href attribute
        td_element[1] = td_element[1].a["href"]

        # add it to the dictionary
        course_href[td_element[0]] = td_element[1]

    # Return the driver
    return course_href


def scrape_grades(soup):
    # Create a matrix to store the course names, assignment names, and grades
    grades_matrix = []

    # Find the div that contains the grades
    div_element = soup.find(
        'div', {'class': 'container clearfix', 'id': 'containerdiv'})

    grades_wrapper = div_element.find(id='grades_wrapper')

    # Find every div with the role row
    div_rows = grades_wrapper.find_all('div', {'role': 'row'})

    # Get the course name from the soup object
    course_name_div = soup.find('div', {'class': 'navPaletteTitle'})

    # Get the course name from the div
    course_name = course_name_div.text

    # Iterate over the rows
    for row in div_rows:
        try:
            # Find the class cell gradable
            class_cell = row.find('div', {'class': 'cell gradable'})
            # Find all elements under the class cell gradable
            divs = class_cell.find_all()
            # Get the text from the first div
            assignment_name = divs[0].text

            # Find the cell grade div
            grade_cell = row.find('div', {'class': 'cell grade'})
            # Find the class grade in the cell grade div
            grade = grade_cell.find('span', {'class': 'grade'})
            # Get the text of the grade span
            grade_text = grade.text

            # Append the course name, assignment name, and grade to the matrix
            grades_matrix.append([assignment_name, grade_text])
        except:
            pass

    return grades_matrix


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


# Create a main function
def scrapper(username, password):

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(executable_path="/path/to/chromedriver")

    #login to blackboard
    login(driver, username, password)

    # Go to the grades page
    Course_Href = get_course_href(driver)

    # Create a dictionary to store the grades
    all_grades = {}

    # For each href in the dictionary
    for href in Course_Href.values():
        # Append the href to the base url
        href = "https://kettering.blackboard.com" + href
        # Scrape the href
        driver.get(href)
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
        # Create a dic to store the grades
        grades = {}
        # call the scrape grades function
        grades = scrape_grades(soup)

        # Add to the course_href dictionary
        all_grades[course_name] = grades
    
    # Generate the HTML file
    generate_html(all_grades)




