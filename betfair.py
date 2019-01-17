import json

import requests

# TODO Move the request.posts to their own function instead of copies


def login(api_key, username, password):
    url = 'https://identitysso.betfair.com/api/login'
    
    data = {
        'username': username,
        'password': password}
    
    headers = {
        'Accept': 'application/json',
        'X-Application': api_key,
        'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post(
        url=url,
        data=data,
        headers=headers)

    if r.status_code == 200:
        return json.loads(r.text)['token']
    else:
        raise ConnectionError('Your login attempt failed...')


def get_football_events(api_key, session_token):
    endpoint = 'https://api.betfair.com/exchange/betting/rest/v1.0/'
    url = endpoint + 'listEvents/'
    
    data = {
        'filter': {
            'eventTypeIds': [1]}}
    
    headers = {
        'X-Application': api_key,
        'X-Authentication': session_token,
        'Content-Type': 'application/json'}

    r = requests.post(
        url=url,
        data=json.dumps(data),  # Not sure why this expects dumped JSON
        headers=headers)

    if r.status_code == 200:
        return json.loads(r.text)
    else:
        raise ConnectionError('Something went wrong trying to get the football '
                              'events...')


def get_market_data(api_key, session_token, events):
    endpoint = 'https://api.betfair.com/exchange/betting/rest/v1.0/'
    url = endpoint + 'listMarketBook/'

    headers = {
        'X-Application':api_key,
        'X-Authentication':session_token,
        'Content-Type':'application/json'}

    for event in events:
        id = event['event']['id']
        data = {
            'eventIds': [id]}  # TODO Something is missing here, faultstring DSC-0018

        r = requests.post(
            url=url,
            data=json.dumps(data),  # Not sure why this expects dumped JSON
            headers=headers)

        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise ConnectionError('Something went wrong trying to get the '
                                  'market data...')


with open('SECRET-api-keys.json') as json_keys:
    betfair_keys = json.load(json_keys)['betfair']
    json_keys.close()

if __name__ == '__main__':
    try:
        print('Betfair: Logging in...')
        session_token = login(
            api_key=betfair_keys['api_key'],
            username=betfair_keys['username'],
            password=betfair_keys['password'])

        print('Betfair: Retreiving all football events...')
        football_events = get_football_events(
            api_key=betfair_keys['api_key'],
            session_token=session_token)

        print('Betfair: Retreiving market data for those events...')
        market_data = get_market_data(
            api_key=betfair_keys['api_key'],
            session_token=session_token,
            events=football_events)

        print('Betfair: Retreived all information. Now what?')

    except Exception as e:
        print('Betfair: ' + e.__class__.__name__ + ' - ' + str(e))
