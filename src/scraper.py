# Import the necessary modules
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

# Create an instance of ChromeOptions
chrome_options = Options()

# Add the headless flag
chrome_options.add_argument("--headless")

# Create a Chrome webdriver instance
driver = webdriver.Chrome(chrome_options=chrome_options)


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

    # Create a dictionary to store the grades
    grades = {}

    # Find the div that contains the grades
    div_element = soup.find(
        'div', {'class': 'container clearfix', 'id': 'containerdiv'})

    grades_wrapper = div_element.find(id='grades_wrapper')

    # Find every div with the role row
    div_rows = grades_wrapper.find_all('div', {'role': 'row'})

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
            # Get the text from the grade
            grade = grade.text

            if not grade.replace('.', '').isdigit():
                # If grade is not a number then it is a letter grade and return the letter grade
                # Add the class name and grade to the dictionary
                grades[assignment_name] = grade
                # Continue to the next iteration
                continue

            # Find the pointsPossible clearfloats
            points_possible = row.find(
                'span', {'class': 'pointsPossible clearfloats'})
            # Get the text from the points possible
            points_possible = points_possible.text

            # Remove the / from the points possible
            points_possible = points_possible.replace("/", "")

            # Divide points by points possible
            grade = float(grade) / float(points_possible)

            # Add the class name and grade to the dictionary
            grades[assignment_name] = grade
        except Exception as e:
            # Do nothing
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

    # Add a table row for each course
    for course, grade in grades.items():
        html_code += "<tr>\n"
        html_code += "<td>{}</td>\n".format(course)
        html_code += "<td>{}</td>\n".format(grade)
        html_code += "</tr>\n"

    # Close the table
    html_code += "</table>\n"

    # Close the body and HTML tags
    html_code += "</body>\n"
    html_code += "</html>\n"

    # Save the HTML code to a file
    with open("grades.html", "w") as f:
        f.write(html_code)


# Create a main function
def main():

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(executable_path="/path/to/chromedriver")

   

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

    print("Done")


# Call the main function
if __name__ == "__main__":
    main()
