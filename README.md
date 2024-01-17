# Project Status
[![CodeQL](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/codeql.yml/badge.svg)](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/codeql.yml)
[![Docker Image CI](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/docker-image.yml/badge.svg)](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/docker-image.yml)
[![Run Behave Tests](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/BDD-Tests.yml/badge.svg)](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/BDD-Tests.yml)
[![Run Blackboard Session Tests](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/Unit-Tests.yml/badge.svg)](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/Unit-Tests.yml)
# Archive-Me

Archive Me is a tool for students to easily archive and track their course materials on Blackboard. It helps students store and organize their coursework for long-term access and reference. This tool is useful for college students to preserve their academic records.

This platform is specifically designed for Kettering University students to extract their course information from Blackboard. It uses session requests and Python to automate the login process and extract the necessary data. Please note that this tool is only intended for use by Kettering University students. I apologize for any inconvenience this may cause to users from other institutions.

## Background

Archive-Me is a project I developed in between work and school rotations to work on my full-stack application development. This project is hosted on a Raspberry Pi 4 using a combination of Github Actions, Watchtower, and Portainer. I automated the build and deployment of updates based on PRs and updates to Main. Below is a system diagram.

![System Diagram](https://github.com/TheManWhoLikesToCode/Archive-Me/blob/main/System-Diagram.png)

## Features

- Automated login

- Course information extraction

- Data organization

Intended for Kettering University students: This tool is specifically designed for use by students at Kettering University and may not be compatible with other institutions.

    
## Usage/Demo

**Demo:** ![Archive Demo](https://github.com/TheManWhoLikesToCode/Archive-Me/blob/main/frontend/static/archive-demo.gif)

Try Archive-Me out [here!](https://archive-me.net)


## Authors

- [@TheManWhoLikesToCode](https://github.com/TheManWhoLikesToCode)

## Description
Archive Me is a Python-based tool specifically designed for Kettering University students to efficiently archive and manage their course materials and grades on Blackboard. By leveraging session requests for automated login and web navigation, along with Beautiful Soup for parsing web content, it extracts detailed course information and organizes it for easy access and long-term reference. Try it out [here](https://archive-me.net/).
