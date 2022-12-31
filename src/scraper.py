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


# Create afunction to scrape the grades page
def scrape_courses(driver):
    # Get the HTML source code of the page
    html = driver.page_source

    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Select the div element with the id "_4_1termCourses__208_1"
    div_element = soup.find(id="_4_1termCourses__208_1")

    # Select the unordered list inside the div element
    ul_element = div_element.ul

    # Select all the list item elements inside the unordered list
    li_elements = ul_element.find_all("li")

    # Create an empty list to store the courses
    courses = []

    # Iterate over the list item elements
    for li_element in li_elements:
        # Select the anchor element inside the list item element
        a_element = li_element.a

        # Get the text content of the anchor element, which is the name of the course
        course_name = a_element.text

        # Add the course name to the list of courses
        courses.append(course_name)

    for course in courses:
        print(course)

    return courses


def go_to_grades(driver):

    # Get the HTML source code of the page
    html = driver.page_source

    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find the unordered list with the class "portletList"
    ul_element = soup.find("ul", class_="portletList")

    # Find the list item element that contains the "My Grades" link
    li_element = ul_element.find("a", text="My Grades")

    # Get the href attribute of the anchor element, which is the URL of the "My Grades" page
    my_grades_url = li_element["href"]

    # Append the base URL to the relative URL
    my_grades_url = "https://kettering.blackboard.com" + my_grades_url

    # Navigate to the "My Grades" page
    driver.get(my_grades_url)

    # Get the HTML source code of the page using the my grades URL
    html = driver.page_source

    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find the iframe element
    iframe = soup.find('iframe', {'class': 'cloud-iframe', 'id': 'mybbCanvas'})

    # Get the src attribute of the iframe
    iframe_src = iframe['src']

    # Append the base URL to the relative URL
    iframe_src = "https://kettering.blackboard.com" + iframe_src

    # go to the iframe
    driver.get(iframe_src)

    # Get the HTML source code of the page
    html = driver.page_source

    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Return the driver
    return soup

def scrape_grades(soup):
    # Find the div id left_stream_mygrades
    parent_div = soup.find("div", id="left_stream_mygrades")

    # Find all div elements under the left_stream_mygrades
    divs = parent_div.find_all("div")

    # Print the bb:rhs attribute of each div
    for div in divs:
      print(div['bb:rhs'])



# Create a main function
def main():

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(executable_path="/path/to/chromedriver")


    # Scrape courses
    courses = scrape_courses(driver)

    # Go to the grades page
    grades_page = go_to_grades(driver)

    # scrape the grades page
    scrape_grades(grades_page)

    print("Pause")

    # end main function


# Call the main function
if __name__ == "__main__":
    main()
