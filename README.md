
# Blackboard Scrapper


The Blackboard Scrapper is a tool for students to easily archive and track their course materials and grades from Blackboard. It helps students store and organize their coursework for long-term access and reference. This scraper is useful for college students preserving their academic record and high schoolers preparing for future studies.-

This web scraper is specifically designed for kettering University students to extract their course information from the Blackboard login page. It uses the Selenium webdriver and Python to automate the login process and extract the necessary data. Please note that this tool is only intended for use by Kettering University students. I apologize for any inconvenience this may cause to users from other institutions.
## Features

- Automated login: The scraper uses Selenium and Python to log in to the Blackboard site automatically, allowing students to extract their course information without having to manually enter their login credentials.

- Course information extraction: The scraper extracts information about the student's courses, including the links to the grades pages and the names and grades of each assignment.

- Data organization: The scraper organizes the extracted data, making it easy for students to access and reference their course materials and grades.

- Long-term access: The scraper allows students to store and archive their course materials and grades, providing long-term access to this information.

- Intended for Kettering University students: This tool is specifically designed for use by students at kettering University and may not be compatible with other institutions.


## Installation

Before you can run this project, you will need to install the following dependencies:

- Python 3.6 or later
- Selenium
- Beautiful Soup
- Requests

You can install these dependencies by running the following commands:

- pip install selenium
- pip install beautifulsoup4
- pip install requests

    
## Usage/Examples

There are currently two working functions in my code. A scrape_content_from_blackboard function that goes through each of your courses and downloads all of the avaliable content. Theres scrape_grades_from_blackboard which goes through each of your courses and gets your grades for each assignment and makes a html file to display your results

scrape_content_from_blackboard("username", "password")


scrape_grades_from_blackboard("username", "password")




## Screenshots

TODO
![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


## Authors

- [@TheManWhoLikesToCode](https://github.com/TheManWhoLikesToCode)


