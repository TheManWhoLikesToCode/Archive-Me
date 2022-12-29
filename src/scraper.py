import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTabWidget


class App(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window properties
        self.setWindowTitle("Blackboard Login")
        self.setGeometry(100, 100, 400, 200)

        # Create the username and password fields
        self.username_field = QLineEdit(self)
        self.password_field = QLineEdit(self)
        self.password_field.setEchoMode(QLineEdit.Password)

        # Create the login button
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)

        # Create the tab widget
        self.tab_widget = QTabWidget(self)

        # Create the layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Username:", self))
        layout.addWidget(self.username_field)
        layout.addWidget(QLabel("Password:", self))
        layout.addWidget(self.password_field)
        layout.addWidget(self.login_button)
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def login(self):

        # Get the username and password from the fields
        username = self.username_field.text()
        password = self.password_field.text()



        # Call the scrappy() function to get the course list
        course_list = scrappy(username, password)

        # Create a new tab for the course list
        self.tab_widget.addTab(QLabel(course_list), "Course List")


def scrappy(username, password):
    # Import the necessary modules
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup
    import time

    # Create a webdriver object and set the desired options
    driver = webdriver.Chrome(executable_path="/path/to/chromedriver")
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




    # Wait here for further instructions
    time.sleep(100)


app = QApplication([])
login_window = App()
login_window.show()
app.exec_()



