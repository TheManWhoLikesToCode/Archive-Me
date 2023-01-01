# Import the necessary modules
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time


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


def scrapper(driver):

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
    grades = {}

    # Iterate over the rows and get the href attribute of the anchor element
    for row in grade_rows:
        # look under td for name of course and grade link
        td_element = row.find_all("td")

        # For element one get the text
        td_element[0] = td_element[0].text

        # For element two get the href attribute
        td_element[1] = td_element[1].a["href"]

        # add it to the dictionary
        grades[td_element[0]] = td_element[1]

    # Return the driver
    return grades


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
        # Find the class cell gradable
        class_cell = row.find('div', {'class': 'cell gradable'})
        # Get the a tag from the class cell
        a_tag = class_cell.find('a')
        # Get the text from the a tag
        assignment_name = a_tag.text
        # Find the cell grade div
        grade_cell = row.find('div', {'class': 'cell grade'})
        # Find the class grade in the cell grade div
        grade = grade_cell.find('span', {'class': 'grade'})
        # Get the text from the grade
        grade = grade.text

        # If the grade is not a number
        if not grade.isnumeric():
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
        grade = int(grade) / int(points_possible)

        # Add the class name and grade to the dictionary
        grades[assignment_name] = grade

    return grades


# Create a main function
def main():

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(executable_path="/path/to/chromedriver")


    # Go to the grades page
    Course_Href = scrapper(driver)

    # Print courses
    for course in Course_Href:
        print(course)

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
        # Create a dic to store the grades
        grades = {}
        # call the scrape grades function
        grades = scrape_grades(soup)

        # Add the grades to the all_grades dictionary
        all_grades.update(grades)

    print("Pause")

    # end main function


# Call the main function
if __name__ == "__main__":
    main()
