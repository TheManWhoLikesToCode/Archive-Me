import requests

# Ping URL function
def ping_url(url):
    try:
        r = requests.get(url)
        return r.status_code
    except Exception as e:
        return e


