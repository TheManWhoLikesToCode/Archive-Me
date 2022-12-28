def scrappy(username, password):
    # Import the necessary modules
    from selenium import webdriver
    from selenium.webdriver.common.by import By

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

    # Wait for the redirect to occur
    if driver.current_url != "https://blackboard.kettering.edu/webapps/login/":
        # On the redirected page accept the cookies policy
        cookies_button = driver.find_element(By.ID, "agree_button")
        cookies_button.click()

        # Find the list items that contain the course information
        course_items = driver.find_elements_by_css_selector(
            ".portletList-img.courseListing.coursefakeclass.u_indent li")

        # Extract the text of the 'a' element within each list item
        courses = []
        for item in course_items:
            course_link = item.find_element(By.TAG_NAME, "a")
            course_text = course_link.text
            courses.append(course_text)

        print(courses)


