import requests
from bs4 import BeautifulSoup


# Ping URL function
def ping_url(url):
    try:
        r = requests.get(url)
        return r.status_code
    except Exception as e:
        return e


# Login function
def login(session, url, username, password):
    # set up the payload
    payload = {'user_id': username, 'password': password}

    # Make the request
    r = session.post(url + 'webapps/login/', data=payload)

    # Check if login was successful
    if r.url == url + '/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1':
        print('Login successful!')
        return True
    elif r.url == url + 'webapps/login/':
        print('Login failed!')
        return False
    else:
        print('An error occurred!')
        return False

# Get the course IDs of the courses the user is enrolled in


def get_course_content_links(session, url, course_id, content_id):
    # Set the URL of the course content page
    content_url = url + '/webapps/blackboard/content/listContent.jsp?course_id=' + \
        course_id + '&content_id=' + content_id

    # Make a GET request to the course content page
    response = session.get(content_url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the links to the content files
    links = soup.find_all('a', {'class': 'item'})

    # Create a list to store the URLs of the content files
    file_urls = []

    # Loop through the links
    for link in links:
        # Get the href attribute of the link
        href = link.get('href')

        # If the href attribute contains the word "listContent" it is a link to a subfolder
        if 'listContent' in href:
            # Get the URL of the subfolder
            url = href.split('?', 1)[0]
            # Get the ID of the subfolder
            id = href.split('?', 1)[1].split('=')[1]

            # Get the file URLs in the subfolder
            subfolder_urls = get_course_content_links(
                session, url, course_id, id)

            # Add the file URLs in the subfolder to the list of file URLs
            file_urls.extend(subfolder_urls)

        # If the href attribute contains the word "content" it is a link to a file
        elif 'content' in href:
            # Get the URL of the file
            url = href.split('?', 1)[0]
            # Get the ID of the file
            id = href.split('?', 1)[1].split('=')[1]

            # Get the download URL of the file
            file_url = get_file_download_url(session, url, course_id, id)

            # Add the download URL to the list of file URLs
            file_urls.append(file_url)

    return file_urls


def get_file_download_url(session, url, course_id, content_id):
    # Set the URL of the file download page
    download_url = url + '/webapps/blackboard/content/launchLink.jsp?course_id=' + \
        course_id + '&content_id=' + content_id

    # Make a GET request to the file download page
    response = session.get(download_url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the link to the file
    link = soup.find('a', {'class': 'resourceUrl'})

    # Get the href attribute of the link
    href = link.get('href')

    return href

# Get the download URL of a file


def download_file(session, url, file_url):
    file_response = session.get(file_url)
    if file_response.status_code == 200:
        return file_response.content
    else:
        raise Exception("An error occurred while downloading the file")


def download_course_content(username, password):
    # Set the URL you want to scrape
    url = 'https://blackboard.kettering.edu/'

    # Create a session to persist cookies
    session = requests.Session()

    # Attempt to login
    if login(session, url, username, password):
        # Get the course IDs and content IDs of the courses the user is enrolled in
        courses = get_course_ids(session, url)

        # Download the course content for each course
        for course in courses:
            course_id = course['course_id']
            content_id = course['content_id']
            print(f'Downloading course content for course {course_id}...')
            links = get_course_content_links(
                session, url, course_id, content_id)
            for link in links:
                file_url = link['file_url']
                file_name = link['file_name']
                download_file(session, url, file_url, file_name)
                print(f'  Downloaded {file_name}')
        print('Download complete!')
    else:
        print('Login failed!')
