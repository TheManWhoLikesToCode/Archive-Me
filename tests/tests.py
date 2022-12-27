def test_web_scraper(download_course_content):
    # Set your login credentials
    username = 'your_username'
    password = 'your_password'

    # Set the course and content IDs
    course_id = '_NNNNN_1'
    content_id = '_YYYYY_1'

    # Call the web scraper function
    download_course_content(username, password, course_id, content_id)

