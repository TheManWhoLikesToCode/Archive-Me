import mimetypes
import os
import logging
import re
from bs4 import BeautifulSoup
from requests import Session
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from playwright.sync_api import sync_playwright


class BlackboardSession:
    def __init__(self, username=None, password=None):
        self.username = username or os.environ.get('USERNAME', 'Free8864')
        self.password = password or os.environ.get(
            'PASSWORD', '#CFi^F6TTwot2j')
        self.session = self._create_session()

    def _create_session(self):
        retries = Retry(total=5, backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
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

    def _send_post_request(self, url, data, allow_redirects=True):  # Added parameter here
        return self.session.post(url, data=data, allow_redirects=allow_redirects)

    def _get_request(self, url):
        return self.session.get(url)

    def _save_response_to_file(self, response, filename='response.html'):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
        logging.info(f"Response saved to '{filename}'.")

    def login(self):
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

            # Save response to file
            self._save_response_to_file(
                login_send_response, filename='login.html')

            if login_send_response.status_code != 200:
                raise Exception("Final POST request failed.")
            logging.info("Login successful.")

        except Exception as e:
            logging.error(f"An error occurred during login: {e}")

    def enable_instructors(self):
        try:
            get_url = "https://kettering.blackboard.com/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1&forwardUrl=edit_module%2F_4_1%2Fbbcourseorg%3Fcmd%3Dedit&recallUrl=%2Fwebapps%2Fportal%2Fexecute%2Ftabs%2FtabAction%3Ftab_tab_group_id%3D_1_1"
            get_response = self._get_request(get_url)

            # Save response to file
            self._save_response_to_file(get_response, filename='get.html')

            if get_response.status_code != 200:
                raise Exception("GET request failed.")

            url = "https://kettering.blackboard.com/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1&forwardUrl=proc_edit/_4_1/bbcourseorg&recallUrl=%2Fwebapps%2Fportal%2Fexecute%2Ftabs%2FtabAction%3Ftab_tab_group_id%3D_1_1"
            payload = {
                'tab_tab_group_id': '_1_1',
                'forwardUrl': 'proc_edit/_4_1/bbcourseorg',
                'blackboard.platform.security.NonceUtil.nonce': '',
                'recallUrl': '/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1',
                'cmd': 'processEdit',
                'serviceLevel': '',
                'termDisplayOrder': '_254_1',
                'amc.groupbyterm': 'true',
                'selectAll_254_1': 'true',
                'amc.showterm._254_1': 'true',
                'termCourses__254_1': 'true',
                'amc.showcourse._51671_1': 'true',
                'amc.showcourseid._51671_1': 'true',
                'amc.showinstructors._51671_1': 'true',
                'amc.showcourse._51672_1': 'true',
                'amc.showcourseid._51672_1': 'true',
                'amc.showinstructors._51672_1': 'true',
                'amc.showcourse._51629_1': 'true',
                'amc.showcourseid._51629_1': 'true',
                'amc.showinstructors._51629_1': 'true',
                'amc.showcourse._51904_1': 'true',
                'amc.showcourseid._51904_1': 'true',
                'amc.showinstructors._51904_1': 'true',
                'amc.showcourse._51945_1': 'true',
                'amc.showcourseid._51945_1': 'true',
                'amc.showinstructors._51945_1': 'true',
                'amc.url.name.1': '',
                'amc.url.url.1': '',
                'amc.url.name.2': '',
                'amc.url.url.2': '',
                'amc.url.name.3': '',
                'amc.url.url.3': '',
                'amc.url.name.4': '',
                'amc.url.url.4': '',
                'amc.url.name.5': '',
                'amc.url.url.5': '',
                'bottom_Submit': 'Submit'
            }
            enable_instructors_response = self._send_post_request(
                get_response.url, data=payload, allow_redirects=False)

            # Save response to file
            self._save_response_to_file(
                enable_instructors_response, filename='enable_instructors.html')

            if enable_instructors_response.status_code == 302:  # Successful redirection
                redirected_url = enable_instructors_response.headers['Location']
                logging.info(
                    f"Successful POST request. Redirected to: {redirected_url}")
            else:
                logging.error(
                    f"POST request failed with status code: {enable_instructors_response.status_code}")

        except Exception as e:
            logging.error(f"An error occurred enabling instructors: {e}")

    def get_courses(self):
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
            self._save_response_to_file(
                get_courses_response, filename='courses.html')
            logging.info("Courses retrieved and saved.")

            # Parse the response using Beautiful Soup with lxml parser
            soup = BeautifulSoup(get_courses_response.content, 'lxml')

            try:
                div_4_1 = soup.find("div", id="_4_1termCourses__254_1")
                courses_list = div_4_1.find_all("ul")[0].find_all("li")
            except Exception as e:
                logging.error(f"Error finding course list: {e}")
                return {}

            # Extract and store links
            hrefs = {course.text.strip(): course.find("a")["href"].strip()
                     for course in courses_list if course.find("a") and course.find("a").get("href")}

            # Process instructors and format course names
            for course in courses_list:
                try:
                    instructor_name = course.find("div").find(
                        "span", class_="name").text.strip()
                    last_name = instructor_name.split()[-1].rstrip(';')

                    # Extract course details
                    course_code = re.search(
                        r'\(([A-Z]{2}-\d{3}-\d{2}L?)\)', course.text)
                    if course_code:
                        course_code = course_code.group(1)
                        # Extract season and year
                        season_year_match = re.search(
                            r'(Fall|Spring|Summer|Winter)\s+\d{4}', course.text)
                        if season_year_match:
                            season_year = season_year_match.group()
                            # Format course name
                            formatted_course_name = f"{course_code}, {last_name}, {season_year}"
                            # Add formatted course name to hrefs dictionary
                            hrefs[formatted_course_name] = hrefs.pop(
                                course.text.strip())
                except Exception as e:
                    logging.error(
                        f"Error processing instructor for course {course.text.strip()}: {e}")
                    continue

            self.courses = hrefs

        except Exception as e:
            logging.error(f"An error occurred while getting courses: {e}")

    def download_and_save_file(self, course_name, assignment_name, url):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if os.path.basename(current_dir) != 'backend':
                session_files_path = os.path.join(current_dir, 'backend', 'Session Files')
                docs_path = os.path.join(current_dir, 'backend', 'docs')
            else:
                session_files_path = os.path.join(current_dir, 'Session Files')
                docs_path = os.path.join(current_dir, 'docs')

            base_directory = os.path.join(session_files_path, course_name)
            os.makedirs(base_directory, exist_ok=True)

            with requests.Session() as s:
                response = s.get(url)

            content_type = response.headers.get('Content-Type')
            guessed_extension = mimetypes.guess_extension(content_type)

            name, current_extension = os.path.splitext(assignment_name)

            if current_extension:
                mime_of_current_extension = mimetypes.guess_type(assignment_name)[0]
                if mime_of_current_extension == content_type:
                    extension = current_extension
                else:
                    extension = guessed_extension or current_extension
            else:
                if 'html' in content_type or b'<html' in response.content or b'<!DOCTYPE HTML' in response.content or b'<html lang="en-US">' in response.content:
                    extension = '.html'
                else:
                    extension = guessed_extension or '.bin'

            file_path = os.path.join(base_directory, name + extension)

            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"File saved to {file_path}")

    def process_courses_for_downloads(self):
        download_tasks = []

        hrefs = self.courses

        for course, href in hrefs.items():
            course_name = re.sub(r'[\\/:*?"<>|]', '', course.strip("\n"))
            full_url = "https://kettering.blackboard.com" + href
            response = self._get_request(full_url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Look in the sidebar for each selectable link
            course_menu = soup.find(id="courseMenuPalette_contents")
            
            for li in course_menu.find_all("li"):
                href = li.find("a")["href"]
                if href[0] != "/":
                    continue
                full_url = "https://kettering.blackboard.com" + href
                response = self._get_request(full_url)
                self._save_response_to_file(
                    response, filename='meni_item_course_menu.html')
                content_listContainer = soup.find(id="content_listContainer")
                if content_listContainer:
                    for li in content_listContainer.find_all('li'):
                        assignment_name = re.sub(
                            r'[\\/:*?"<>|]', '_', li.text.strip().split("\n")[0] or "Untitled")
                        a = li.select_one('a')
                        if a and a['href'][0] != "h":
                            full_url = "https://kettering.blackboard.com" + \
                                a['href']
                            self.download_and_save_file(self,
                                course_name, assignment_name, full_url)
            
# Usage:
bb_session = BlackboardSession()
bb_session.login()
# bb_session.enable_instructors()
bb_session.get_courses()
bb_session.process_courses_for_downloads()
print(bb_session.courses)
print(bb_session.downloadTasks)
