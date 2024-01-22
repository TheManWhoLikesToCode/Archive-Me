from bs4 import BeautifulSoup
import re

def extract_ids(html):
    soup = BeautifulSoup(html, 'html.parser')
    course_ids = []
    header_ids = []

    # Extracting course IDs
    for div in soup.find_all('div', id=re.compile(r'_4_1termCourses__(\d+_\d+)')):
        course_id_match = re.search(r'_4_1termCourses__(\d+_\d+)', div.get('id', ''))
        if course_id_match:
            course_id = course_id_match.group(1)
            course_ids.append(course_id)

    # Extracting header IDs
    for a in soup.find_all('a', id=re.compile(r'afor_4_1termCourses__(\d+_\d+)')):
        header_id_match = re.search(r'afor_4_1termCourses__(\d+_\d+)', a.get('id', ''))
        if header_id_match:
            header_id = header_id_match.group(1)
            header_ids.append(header_id)

    return course_ids, header_ids

# Example usage
html_content = """<html>
                    <div id="div_4_1">
                        <div class="noItems" style="display:none">All of your courses are hidden.</div>

                        <h3 class="termHeading-coursefakeclass" id="anonymous_element_7">
                            <a id="afor_4_1termCourses__243_1" title="Collapse" href="#" class="itemHead itemHeadOpen"
                                onclick="toggleTermLink('_4_1','termCourses__243_1', 'ebd88f5b-786d-4517-9ea5-cb227d799d4e')">
                                <span class="hideoff">Collapse</span>
                                Summer 2023</a>
                        </h3>
                        <div id="_4_1termCourses__243_1" style="">
                            <h4 class="u_indent" id="anonymous_element_8">Courses where you are: Student</h4>
                            <ul class="portletList-img courseListing coursefakeclass u_indent">
                                <li>
                                    <img alt=""
                                        src="https://learn.content.blackboardcdn.com/3900.82.0-rel.45+82d6e90/images/ci/icons/bookopen_li.gif"
                                        width="12" height="12">
                                    <a href=" /webapps/blackboard/execute/launcher?type=Course&amp;id=_51316_1&amp;url="
                                        target="_top">35221.202303: Culminating Undergraduate Experience: Thesis (CILE-400-01) Summer
                                        2023</a>
                                    <div class="courseInformation">
                                        <span class="courseRole">
                                            Instructor:
                                        </span>
                                        <span class="name">Michelle Gebhardt;&nbsp;&nbsp;</span>
                                    </div>
                                </li>
                            </ul>
                        </div>
                        <h3 class="termHeading-coursefakeclass" id="anonymous_element_9">
                            <a id="afor_4_1termCourses__259_1" title="Collapse" href="#" class="termToggleLink itemHead itemHeadOpen"
                                onclick="toggleTermLink('_4_1','termCourses__259_1', 'ebd88f5b-786d-4517-9ea5-cb227d799d4e')">
                                <span class="hideoff">Collapse</span>
                                Winter 2024</a>
                        </h3>
                        <div id="_4_1termCourses__259_1" style="">
                            <h4 class="u_indent" id="anonymous_element_10">Courses where you are: Student</h4>
                            <ul class="portletList-img courseListing coursefakeclass u_indent">
                                <li>
                                    <img alt=""
                                        src="https://learn.content.blackboardcdn.com/3900.82.0-rel.45+82d6e90/images/ci/icons/bookopen_li.gif"
                                        width="12" height="12">
                                    <a href=" /webapps/blackboard/execute/launcher?type=Course&amp;id=_52268_1&amp;url="
                                        target="_top">15664.202401: COOP-002-01: Co-op Educat Exp - Employed - WINTER</a>
                                    <div class="courseInformation">
                                        <span class="courseRole">
                                            Instructor:
                                        </span>
                                        <span class="noItems">
                                            No Instructors.
                                        </span>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </html>"""  # Replace with your actual HTML content
course_ids, header_ids = extract_ids(html_content)
print("Course IDs:", course_ids)
print("Header IDs:", header_ids)
