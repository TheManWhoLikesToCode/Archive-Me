# Project Status
[![CodeQL](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/codeql.yml/badge.svg)](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/codeql.yml)
[![Docker Image CI](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/docker-image.yml/badge.svg)](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/docker-image.yml)
[![Run Behave Tests](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/BDD-Tests.yml/badge.svg)](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/BDD-Tests.yml)
[![Run Blackboard Session Tests](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/Unit-Tests.yml/badge.svg)](https://github.com/TheManWhoLikesToCode/Archive-Me/actions/workflows/Unit-Tests.yml)

# Archive-Me
Archive Me is a tool for students to easily archive and track their course materials on Blackboard. It helps students store and organize their coursework for long-term access and reference. This tool is useful for college students to preserve their academic records.

This platform is specifically designed for Kettering University students to extract their course information from Blackboard. It uses session requests and Python to automate the login process and extract the necessary data. Please note that this tool is only intended for use by Kettering University students. I apologize for any inconvenience this may cause to users from other institutions.

## Background

I developed Archive-Me, a full-stack application project, during my breaks from work and school. It's hosted on a Raspberry Pi 4 and utilizes Github Actions, Watchtower, and Portainer for seamless integration. The system automates build and deployment processes in response to PRs and main branch updates. The application uses NGINX as a reverse proxy to manage incoming traffic and expose specific ports. It routes requests to the uWSGI server, which communicates with the Flask application via WebSocket. A system diagram is provided for detailed architecture.

![System Diagram](https://github.com/TheManWhoLikesToCode/Archive-Me/blob/main/System-Diagram.png)

The diagram below displays how the user authentication process is employed by Archive-Me, detailing the steps involved in authenticating a user's access to various resources.

![User Authentication](https://github.com/TheManWhoLikesToCode/Archive-Me/blob/main/Authentication-Flow.png)

Below is the session diagram which goes more indepth with how user sessions are handled.

![Session Diagram](https://github.com/TheManWhoLikesToCode/Archive-Me/blob/main/Session.png)


## Features

- Automated login

- Course information extraction

- Data organization

Intended for Kettering University students: This tool is specifically designed for use by students at Kettering University and may not be compatible with other institutions.

    
## Usage/Demo

**Demo:** ![Archive Demo](https://github.com/TheManWhoLikesToCode/Archive-Me/blob/main/frontend/static/archive-demo.gif)

Try Archive-Me out [here!](https://archive-me.net)

## Stats

![Lifetime Users!](https://github.com/TheManWhoLikesToCode/Archive-Me/blob/main/cumulative_unique_visitors.png)

## Authors

- [@TheManWhoLikesToCode](https://github.com/TheManWhoLikesToCode)

## Descripton
Archive Me is a Python-based tool specifically designed for Kettering University students to efficiently archive and manage their course materials and grades on Blackboard. By leveraging session requests for automated login and web navigation, along with Beautiful Soup for parsing web content, it extracts detailed course information and organizes it for easy access and long-term reference. Try it out [here](https://archive-me.net/).
