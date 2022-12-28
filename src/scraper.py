# Import the necessary modules
from     import webdriver
from selenium.webdriver.common.by import By

# Create a webdriver object and set the desired options
driver = webdriver.Chrome(executable_path="/path/to/chromedriver")
driver.implicitly_wait(10) # Wait for up to 10 seconds for elements to become available

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

username = "Free8864"
password = "P@ssword00!?!?!"

username_field.send_keys(username)
password_field.send_keys(password)


print("Logging in...")



