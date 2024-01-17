import csv
import os
import requests
import logging
from datetime import datetime
import matplotlib.dates as mdates
from urllib3.util.retry import Retry
from matplotlib import pyplot as plt
from requests.adapters import HTTPAdapter

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Config:
    API_TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN')
    ZONE_TAG = os.environ.get('CLOUDFLARE_ZONE_TAG')
    RETRY_STRATEGY = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    URL = 'https://api.cloudflare.com/client/v4/graphql/'


def fetch_unique_visitors(api_token, zone_tag, date):
    """
    Fetch unique visitors from the GraphQL API for a specific date.
    """
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=Config.RETRY_STRATEGY))
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    query = {
        "query": """
            {
                viewer {
                    zones(filter: { zoneTag: "%s" }) {
                        httpRequests1dGroups(limit: 100, filter: { date_geq: "%s" }) {
                            sum {
                                bytes
                            }
                            uniq {
                                uniques
                            }
                        }
                    }
                }
            }
        """ % (zone_tag, date)
    }

    try:
        response = session.post(Config.URL, headers=headers, json=query)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as errh:
        logging.error(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logging.error(f"Error: {err}")


def get_total_users():
    """
    Get the total number of users from the CSV file.
    """
    total_users = 0
    with open('unique_visitors.csv', 'r') as f:
        next(f)  # Skip the header line
        for line in f:
            _, value = line.strip().split(',')
            total_users += int(value)
    return total_users


def plot_total_users():
    dates = []
    cumulative_values = []
    total = 0

    with open('unique_visitors.csv', 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header
        for row in csv_reader:
            date = datetime.strptime(row[0], '%d %b %Y')
            value = int(row[1])
            total += value  # Cumulative sum
            dates.append(date)
            cumulative_values.append(total)

    plt.figure(figsize=(10, 6))
    plt.plot(dates, cumulative_values, marker='o')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.gcf().autofmt_xdate()  # Rotation
    plt.xlabel('Date')
    plt.ylabel('Cumulative Unique Visitors')
    plt.title('Cumulative Unique Visitors Over Time')
    plt.grid(True)

    # Remove the existing file if it exists
    if os.path.exists('cumulative_unique_visitors.png'):
        os.remove('cumulative_unique_visitors.png')

    plt.savefig('cumulative_unique_visitors.png')


def update_csv_with_visitors(api_token, zone_tag):
    try:
        date = datetime.today().strftime('%Y-%m-%d')
        visitors_data = fetch_unique_visitors(api_token, zone_tag, date)
        if visitors_data:
            visitors = visitors_data['data']['viewer']['zones'][0]['httpRequests1dGroups'][0]['uniq']['uniques']
            logging.info(f"Unique visitors for {date}: {visitors}")

            # Adjust the date format to 'DD MMM YYYY'
            formatted_date = datetime.today().strftime('%d %b %Y').upper()

            # Check if today's date is already in the CSV
            with open('unique_visitors.csv', 'r+') as f:
                lines = f.readlines()
                last_line = lines[-1] if lines else ''
                if formatted_date in last_line:
                    # Update the existing entry
                    lines[-1] = f"{formatted_date},{visitors}\n"
                    f.seek(0)
                    f.writelines(lines)
                else:
                    # Append the new entry
                    f.write(f"\n{formatted_date},{visitors}")
        else:
            logging.error("No data received from API.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def main():
    if not all([Config.API_TOKEN, Config.ZONE_TAG]):
        logging.error("Environment variables are missing.")
        return

    print(get_total_users())
    plot_total_users()
    update_csv_with_visitors(Config.API_TOKEN, Config.ZONE_TAG)


if __name__ == "__main__":
    main()
