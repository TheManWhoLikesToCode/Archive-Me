import os
from requests import Session
from urllib.parse import quote
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# User's credentials from environment variables or secure config


# Retry strategy for network requests
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)

# Create a session with retry strategy
with Session() as session:
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    # Initial URL
    initial_url = "https://blackboard.kettering.edu/"

    try:
        # Navigate to the initial URL without following redirects automatically
        response = session.get(initial_url, allow_redirects=False)

        # Manually handle one redirect if it exists
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers['Location']
            response = session.get(redirect_url)

        # Additional error handling for response status
        response.raise_for_status()

        # Capture the final URL after redirects
        redirect_url = response.url

        # Payload for the first POST request
        first_payload = {
            '_eventId_proceed': ''
        }

        # Send the first POST request to the redirect URL
        first_post_response = session.post(redirect_url, data=first_payload)

        # Check response
        if first_post_response.status_code != 200:
            raise Exception("First POST request failed.")

        # Parse the redirected URL to extract the 'execution' parameter
        execution_value = first_post_response.url.split('execution=')[1].split('&')[0]

        # Payload for the final POST request (with URL-encoded password)
        final_payload = {
            'execution': execution_value,
            'j_username': username,
            'j_password': password,
            '_eventId_proceed': ''
        }

        # Send the final POST request
        final_post_response = session.post(
            first_post_response.url, data=final_payload)

        # Save the response content to a file in a safer way
        with open('response.html', 'w', encoding='utf-8') as file:
            file.write(final_post_response.text)
        logging.info("Response saved to 'response.html'.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
