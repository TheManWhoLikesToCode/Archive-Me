from bs4 import BeautifulSoup
import requests


# Username: Free8864
# Password: P@ssword00!?!?!
def login_and_get_courses(username, password):
    # Send a POST request to the login form with the username and password
    login_url = "https://blackboard.kettering.edu/"
    login_data = {"username": username, "password": password}
    session = requests.Session()
    response = session.post(login_url, data=login_data)

    # Check if the login was successful
    if response.status_code != 200:
        raise Exception("Login failed")

    print("Login successful")

    # Get the HTML source code of the page after logging in
    page_url = "https://kettering.blackboard.com/webapps/portal/execute/tabs/tabAction?tabId=_1_1&tab_tab_group_id=_1_1"
    page_response = session.get(page_url)
    page_html = page_response.text
    print("Got page HTML")

    # Parse the HTML to extract the list of courses
    soup = BeautifulSoup(page_html, "html.parser")
    # TODO Fix this
    courses_element = soup.find("div", id="_4_1termCourses__208_1")
    course_elements = courses_element.find_all("li", class_="course")
    courses = []
    for course_element in course_elements:
        course_name = course_element.find("h3").text
        courses.append({"name": course_name})

    return courses

# Call the login function
print(login_and_get_courses("Free8864", "P@ssword00!?!?!"))
