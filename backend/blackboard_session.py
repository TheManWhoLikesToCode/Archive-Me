import logging
import mimetypes
import time
import os
import re
import zipfile
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BlackboardSession:
    def __init__(self, session_id=None, username=None, password=None, max_threads=100):
        """
        Creates a blackboard session instance.

        Arguements:
        username -- The username of the user to login as.
        password -- The password of the user to login as.
        max_threads -- The maximum number of threads to use for downloading files.

        Returns:
        A BlackboardSession instance.

        """

        self.username = username
        self.password = password
        self.max_threads = max_threads
        self.session_id = session_id
        self.courses = {}
        self.download_tasks = []
        self.is_logged_in = False
        self.instructorsFound = False
        self.courseFound = False
        self.downloadTasksFound = False
        self.zipFound = False
        self.last_activity_time = None
        self.response = None
        self.session = self._create_session()

    def _create_session(self):
        """"

        Creates a session with a retry adapter.

        Returns:
        A session instance with a retry adapter and a pool size of 5 times to
        allow for more connections aka more downloads.

        """
        retries = Retry(total=5, backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries,
                              pool_maxsize=self.max_threads * 5)
        session = Session()
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        return session

    def _get_initial_url_response(self, url):
        return self.session.get(url, allow_redirects=False)

    def _handle_redirect(self, response):
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers['Location']
            return self.session.get(redirect_url)
        return response

    def _send_post_request(self, url, data, allow_redirects=True):
        return self.session.post(url, data=data, allow_redirects=allow_redirects)

    def _get_request(self, url):
        return self.session.get(url)

    def _save_response_to_file(self, response, filename='response.html'):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
        logging.info(f"Response saved to '{filename}'.")

    def set_response(self, response):
        self.response = response

    def get_response(self):
        return self.response

    def get_InstructorsFound(self):
        return self.instructorsFound

    def set_InstructorsFound(self, instructorsFound):
        self.instructorsFound = instructorsFound

    def shutdown(self):
        """

        Clean up resources and delete the session to prevent memory leaks.

        """
        if self.session:
            self.session.close()
            del self.session
            logging.info("Session closed and deleted.")
        else:
            logging.warning("No active session to delete.")

    def scrape(self):

        if self.is_logged_in == False:
            self.response = "Not logged in."
            return

        self.enable_instructors_and_year_season()
        if self.get_InstructorsFound() == False:
            self.response = "No instructors found."

        self.get_courses()
        if self.courseFound == False or len(self.courses) == 0:
            self.response = "No courses found."
            return

        self.get_download_tasks()
        if self.downloadTasksFound == False or len(self.download_tasks) == 0:
            self.response = "Failed to get download tasks."
            return

        file_key = self.download_and_save_file()
        if self.zipFound == False or file_key == None:
            self.response = "Failed to download and save file."
            return

        self.response = None
        self.last_activity_time = time.time()
        return file_key

    def login(self):
        """

        Logs into blackboard using the username and password provided using
        the requests library and saves the session cookies.

        self modifies:
        is_logged_in -- A boolean value indicating if the user is logged in.
        last_activity_time -- The time of the last activity.
        response -- The response of the login attempt.

        """

        if self.is_logged_in == True:
            self.set_response("Already logged in.")
            return

        try:
            initial_url = "https://blackboard.kettering.edu/"
            init_response = self._get_initial_url_response(initial_url)
            init_response = self._handle_redirect(init_response)
            init_response.raise_for_status()

            redirect_url = init_response.url
            first_payload = {'_eventId_proceed': ''}
            int_login_page_response = self._send_post_request(
                redirect_url, data=first_payload)
            if int_login_page_response.status_code != 200:
                raise Exception("First POST request failed.")

            execution_value = int_login_page_response.url.split('execution=')[
                1].split('&')[0]
            final_payload = {
                'execution': execution_value,
                'j_username': self.username,
                'j_password': self.password,
                '_eventId_proceed': ''
            }

            login_send_response = self._send_post_request(
                int_login_page_response.url, data=final_payload)

            # parse the response using Beautiful Soup with html parser
            soup = BeautifulSoup(login_send_response.content, "html.parser")

            try:
                # Log the response of soup to be the response of the users payload
                login_payload_response = soup.find(class_='alert alert-danger')
            except Exception as e:
                logging.error(
                    f"An error occurred while finding the payload response: {e}")

            # If the login_send_response url isn't the same as the login_send_response url
            if login_send_response.url != int_login_page_response.url and login_payload_response == None:
                self.is_logged_in = True
                self.set_response("Login successful.")
            else:
                self.is_logged_in = False
                if login_payload_response:
                    login_payload_response = login_payload_response.text.strip()
                else:
                    login_payload_response = "Login failed."
                self.set_response(login_payload_response)

            self.last_activity_time = time.time()

        except Exception as e:
            logging.error(f"An error occurred during login: {e}")

    def enable_instructors_and_year_season(self):
        """

        Enables instructors & course term year for all courses the user is taking.

        self modifies:
        instructorsFound -- A boolean value indicating if instructors were found.
        last_activity_time -- The time of the last activity.
        response -- The response of the enable instructors attempt.

        """

        if self.is_logged_in == False:
            self.response = "Not logged in."
            return

        try:
            get_url = "https://kettering.blackboard.com/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1&forwardUrl=edit_module%2F_4_1%2Fbbcourseorg%3Fcmd%3Dedit&recallUrl=%2Fwebapps%2Fportal%2Fexecute%2Ftabs%2FtabAction%3Ftab_tab_group_id%3D_1_1"
            try:
                get_response = self._get_request(get_url)

                if get_response.status_code != 200:
                    raise Exception("GET request failed.")

                course_ids = []
                term_ids = []

                # Using beautiful soup get the value from this input #moduleEditForm > input[type=hidden]:nth-child(1)
                soup = BeautifulSoup(get_response.content, "html.parser")
                course_table = soup.find_all(
                    attrs={"id": re.compile(r'blockAttributes_table_jsListFULL_Student_\d+_\d+_body')})
                if not course_table:
                    raise Exception("Course table not found.")

                term_table = soup.find_all(
                    attrs={"id": "termDisplay_table_jsListTermDisplay"})
                if not term_table:
                    raise Exception("Term table not found.")

                course_rows = course_table[0].find_all('tr')
                if not course_rows:
                    raise Exception("Course rows not found.")

                term_rows = term_table[0].find_all('tr')
                if not term_rows:
                    raise Exception("Term rows not found.")

                for row in course_rows:
                    course_id_match = re.search(
                        r'FULL_Student_\d+_\d+_row:_(\d+_\d+)', row.get('id', ''))
                    if course_id_match:
                        course_id = course_id_match.group(1)
                        course_ids.append(course_id)

                for row in term_rows:
                    term_id_match = re.search(
                        r'termDisplay_table_jsListTermDisplay_row:_(\d+_\d+)', row.get('id', ''))
                    if term_id_match:
                        term_id = term_id_match.group(1)
                        term_ids.append(term_id)

                nonce_value = soup.select_one(
                    '#moduleEditForm > input[type=hidden]:nth-child(1)')['value']

                url = "https://kettering.blackboard.com/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1&forwardUrl=proc_edit/_4_1/bbcourseorg&recallUrl=%2Fwebapps%2Fportal%2Fexecute%2Ftabs%2FtabAction%3Ftab_tab_group_id%3D_1_1"
                payload = {
                    'tab_tab_group_id': '_1_1',
                    'forwardUrl': 'proc_edit/_4_1/bbcourseorg',
                    'blackboard.platform.security.NonceUtil.nonce': nonce_value,
                    'recallUrl': '/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1',
                    'cmd': 'processEdit',
                    'serviceLevel': '',
                    'amc.url.name.1': '',
                    'amc.url.url.1': '',
                    'amc.url.name.2': '',
                    'amc.url.url.2': '',
                    'amc.url.name.3': '',
                    'amc.url.url.3': '',
                    'amc.url.name.4': '',
                    'amc.url.url.4': '',
                    'amc.url.name.5': '',
                    'amc.url.url.5': ''

                }

                for course in course_ids:
                    payload['amc.showcourse._' + course] = 'true'
                    payload['amc.showcourseid._' + course] = 'true'
                    payload['amc.showinstructors._' + course] = 'true'

                for term in term_ids:
                    payload['amc.groupbyterm'] = 'true'
                    payload['selectAll_{}'.format(term)] = 'true'
                    payload['amc.showterm._{}'.format(term)] = 'true'
                    payload['termCourses__{}'.format(term)] = 'true'

                payload['bottom_Submit'] = 'Submit'

                enable_instructors_response = self._send_post_request(
                    url, data=payload, allow_redirects=False)

                if enable_instructors_response.status_code == 302:
                    redirected_url = enable_instructors_response.headers['Location']
                    logging.info(
                        f"Successful POST request. Redirected to: {redirected_url}")
                    self.set_InstructorsFound(True)
                else:
                    self.set_InstructorsFound(False)
                    raise Exception("POST request failed.")

                self.last_activity_time = time.time()

            except Exception as e:
                logging.error(
                    f"An error occurred enabling instructors: {e}")
                return

        except Exception as e:
            logging.error(f"An error occurred enabling instructors: {e}")

    def get_courses(self):
        """

        Gets the courses the user is taking and stores in a dictionary 
        contained in the courses attribute. The key is the course name and
        the value is the link to the course.

        self modifies:
        courses -- A dictionary of courses the user is taking.
        courseFound -- A boolean value indicating if courses were found.
        last_activity_time -- The time of the last activity.
        response -- The response of the get courses attempt.

        """

        if self.is_logged_in == False:
            self.response = "Not logged in."
            return

        try:
            form_data = {
                'action': 'refreshAjaxModule',
                'modId': '_4_1',
                'tabId': '_1_1',
                'tab_tab_group_id': '_1_1'
            }
            url = "https://kettering.blackboard.com/webapps/portal/execute/tabs/tabAction"
            get_courses_response = self._send_post_request(url, data=form_data)
            if get_courses_response.status_code != 200:
                raise Exception("POST request failed.")

            # Parse the response using Beautiful Soup
            soup = BeautifulSoup(get_courses_response.content)

            # Check if the user is not enrolled in any courses
            no_courses_text = 'You are not currently enrolled in any courses.'
            if no_courses_text in str(soup):
                self.response = no_courses_text
                return

            course_details = {}
            courses_list = []
            try:
                div_4_1 = soup.find_all(
                    "div", id=re.compile(r'^_4_1termCourses'))
                for div in div_4_1:
                    course_id_match = re.search(
                        r'_4_1termCourses__(\d+_\d+)', div.get('id', ''))
                    if course_id_match:
                        pattern = r'([A-Z]+-[0-9]+-[0-9]+[A-Z]?)|([A-Z]+-[0-9]+)'
                        course_code = re.search(pattern, div.text)
                        course_code = course_code.group()

                        course_id = course_id_match.group(1)
                        course_details[course_code] = course_id
                    courses_list.extend(div.find_all("li"))

            except Exception as e:
                logging.error(f"Error finding course list: {e}")
                return "Error finding course list."

            course_ids = []
            header_ids = []
            season_year = {}

            try:
                # Extracting course IDs
                for div in soup.find_all('div', id=re.compile(r'_4_1termCourses__(\d+_\d+)')):
                    course_id_match = re.search(
                        r'_4_1termCourses__(\d+_\d+)', div.get('id', ''))
                    if course_id_match:
                        course_ids.append(course_id_match.group(1))
                # Extracting header IDs
                for a in soup.find_all('a', id=re.compile(r'afor_4_1termCourses__(\d+_\d+)')):
                    header_id_match = re.search(
                        r'afor_4_1termCourses__(\d+_\d+)', a.get('id', ''))
                    if header_id_match:
                        header_id = header_id_match.group(1)
                        header_ids.append(header_id)

                # Extract the season and year from the header
                for header_id in header_ids:
                    header = soup.find(
                        'a', id=f'afor_4_1termCourses__{header_id}')
                    if header:
                        season_year_match = re.search(
                            r'(Spring|Summer|Fall|Winter)\s+(\d{4})', header.text.strip())
                        if season_year_match:
                            season, year = season_year_match.groups()
                            season_year[header_id] = (season, year)

                # Make a dictionary of course id's and their season and year
                course_season_mapping = {}
                for course_id in course_ids:
                    if course_id in season_year:
                        course_season_mapping[course_id] = season_year[course_id]

            except Exception as e:
                logging.error(f"Error processing course data: {e}")
                return "Error processing course data."

            # Extract and store links
            hrefs = {course.text.strip(): course.find("a")["href"].strip()
                     for course in courses_list if course.find("a") and course.find("a").get("href")}

            if self.get_InstructorsFound() == True:
                # Process instructors and format course names
                for course in courses_list:
                    try:
                        try:
                            instructor_name = course.find("div").find("span", class_="name").text.strip()
                            last_name = instructor_name.split()[-1].rstrip(';')
                            if not last_name:
                                last_name = "No Instructor"
                        except:
                            last_name = "No Instructor"

                        pattern = r'([A-Z]+-[0-9]+-[0-9]+[A-Z]?)|([A-Z]+-[0-9]+)'
                        course_code = re.search(pattern, course.text)

                        course_code = course_code.group()

                        if course_code:
                            course_id = course_details[course_code]
                            season, year = course_season_mapping[course_id]
                            formatted_course_name = f"{course_code}, {last_name}, {season} {year}"
                            # Add formatted course name to hrefs dictionary
                            hrefs[formatted_course_name] = hrefs.pop(
                                course.text.strip())
                    except Exception as e:
                        logging.error(
                            f"Error processing instructor for course {course.text.strip()}: {e}")
                        continue

            self.courses = hrefs
            self.courseFound = True
            self.last_activity_time = time.time()

        except Exception as e:
            self.courseFound = False
            self.response = e
            logging.error(f"An error occurred while getting courses: {e}")

    def download_and_save_file(self):
        """
        Downloads and saves the tasks passed from the get download tasks function.

        self modifies:
        zipFound -- A boolean value indicating if the zip file was found.
        last_activity_time -- The time of the last activity.
        response -- The response of the download and save file attempt.
        """

        if not self.is_logged_in:
            self.response = "Not logged in."
            return

        current_dir = os.path.dirname(os.path.abspath(__file__))
        session_files_path = os.path.join(current_dir, 'backend', 'Session Files') if os.path.basename(
            current_dir) != 'backend' else os.path.join(current_dir, 'Session Files')

        zip_file_name = f'{self.username}_downloaded_content.zip'
        zip_file_path = os.path.join(current_dir, zip_file_name)

        download_tasks = getattr(self, 'download_tasks', [])

        def download_task(task):
            course_name, assignment_name, url = task

            base_directory = os.path.join(session_files_path, course_name)
            os.makedirs(base_directory, exist_ok=True)

            response = self._get_request(url)

            content_type = response.headers.get('Content-Type')
            guessed_extension = mimetypes.guess_extension(content_type)

            name, current_extension = os.path.splitext(assignment_name)

            if current_extension:
                mime_of_current_extension = mimetypes.guess_type(assignment_name)[
                    0]
                extension = current_extension if mime_of_current_extension == content_type else guessed_extension or current_extension
            else:
                if 'html' in content_type or b'<html' in response.content or b'<!DOCTYPE HTML' in response.content or b'<html lang="en-US">' in response.content:
                    return
                extension = guessed_extension or '.bin'

            # Skip download if file type is None
            if extension is None:
                print(
                    f"Skipped downloading {assignment_name} as file type could not be determined.")
                return

            file_path = os.path.join(base_directory, name + extension)

            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"File saved to {file_path}")

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            executor.map(download_task, download_tasks)

        # Create the zip file
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, dirs, files in os.walk(session_files_path):
                for file in files:
                    if file.endswith('.pdf') or file.endswith('.docx'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(
                            file_path, session_files_path)
                        zipf.write(file_path, arcname=arcname)

        self.zipFound = True
        self.last_activity_time = time.time()

        return os.path.relpath(zip_file_path, os.getcwd())

    def get_download_tasks(self):
        """

        Gets a list of download tasks to be executed by collection all of the 
        "downlaodable" coneent from each course.

        self modifies:
        download_tasks -- A list of download tasks to be executed.
        downloadTasksFound -- A boolean value indicating if download tasks were found.
        last_activity_time -- The time of the last activity.
        response -- The response of the get download tasks attempt.

        """

        if self.is_logged_in == False:
            self.response = "Not logged in."
            return

        download_tasks = []

        hrefs = self.courses

        def process_course(course, href):
            course_name = re.sub(r'[\\/:*?"<>|]', '', course.strip("\n"))
            full_url = "https://kettering.blackboard.com" + href
            response = self._get_request(full_url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Look in the sidebar for each selectable link
            course_menu = soup.find(id="courseMenuPalette_contents")

            for li in course_menu.contents:
                try:
                    href = li.find("a")["href"]
                    if href[0] != "/":
                        continue
                    full_url = "https://kettering.blackboard.com" + href
                    response = self._get_request(full_url)
                    soup = BeautifulSoup(response.content, "html.parser")
                    content_listContainer = soup.find(id="containerdiv")

                    if content_listContainer:
                        for content_li in content_listContainer.find_all('li'):
                            assignment_name = re.sub(
                                r'[\\/:*?"<>|]', '_', content_li.text.strip().split("\n")[0] or "Untitled")
                            a = content_li.select_one('.details a')
                            if a and a['href'][0] != "h":
                                full_url = "https://kettering.blackboard.com" + \
                                    a['href']
                                download_tasks.append(
                                    (course_name, assignment_name, full_url))
                except Exception as e:
                    logging.error(
                        f"Error processing course {course_name}: {e}")
                    continue

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            executor.map(process_course, hrefs.keys(), hrefs.values())

        self.download_tasks = download_tasks
        self.downloadTasksFound = True
        self.last_activity_time = time.time()
