import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout


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

        # Create the layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Username:", self))
        layout.addWidget(self.username_field)
        layout.addWidget(QLabel("Password:", self))
        layout.addWidget(self.password_field)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def login(self):
        # Get the username and password from the fields
        username = self.username_field.text()
        password = self.password_field.text()

        # Call the scrappy() function with the username and password
        scrappy(username, password)


def scrappy(username, password):
    # Import the necessary modules
    from selenium import webdriver
    from selenium.webdriver.common.by import By
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

    # The redirect has occurred, so we can now login

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

    div = driver.find_element(By.ID, "_4_1termCourses__208_1")
    # Print the course list
    print(div.text)


app = QApplication([])
login_window = App()
login_window.show()
app.exec_()



