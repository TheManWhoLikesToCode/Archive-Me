import requests


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



