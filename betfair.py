from datetime import datetime
import json

import pickle
import requests


def login(api_key, username, password):
    print('Betfair: Logging in...')
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


def betfair_request(api_key, session_token, method, data):
    endpoint = 'https://api.betfair.com/exchange/betting/rest/v1.0/'
    url = endpoint + method + '/'

    headers = {
        'X-Application':api_key,
        'X-Authentication':session_token,
        'Content-Type':'application/json'}

    r = requests.post(
        url=url,
        data=data,
        headers=headers)

    if r.status_code == 200:
        return json.loads(r.text)
    else:
        raise ConnectionError(
            'Something went wrong requesting the {} method with the following '
            'data:\n{}'.format(
                method,
                data))

def get_football_events(api_key, session_token):
    print('Betfair: Retreiving all future football events...')

    method = 'listEvents'
    now = datetime.now().isoformat()
    data = json.dumps({
        'filter': {
            'eventTypeIds': [1]},  # 1 = football
            'marketStartTime': {'from': now},
        'sort':'FIRST_TO_START'})  # Not sure why this expects dumped JSON

    return betfair_request(api_key, session_token, method, data)


def get_all_match_odds(api_key, session_token, events):
    numEvents = len(events)
    print('Betfair: Retreiving match odds for all {} events...'.format(numEvents))

    event_odds = []

    for event in events:
        event_match_odds = get_event_match_odds(
            api_key,
            session_token,
            event['event']['id'])

        event_odds.append({
            'event_name': event['event']['name'],
            'lay_odds': event_match_odds})

    return event_odds


def get_event_match_odds(api_key, session_token, eventId):
    print('Betfair: \tRetreiving match odds for event {}...'.format(
        eventId))

    odds_market = get_event_market_catalogue(
        api_key,
        session_token,
        eventId,
        marketTypeCode='MATCH_ODDS')

    if len(odds_market) > 0:
        # i.e. if a Match Odds market was found for the event
        odds_market = odds_market[0]

        market_odds = []

        for runner in odds_market['runners']:
            marketId = odds_market['marketId']
            runnerId = runner['selectionId']

            runner_book = get_runner_book(
                api_key,
                session_token,
                marketId,
                runnerId)

            if len(runner_book[0]['runners'][0]['ex']['availableToLay']) > 0:
                # i.e. if there are any open bets on the exchange to match
                back_bet = runner['runnerName'] + ' to Win'
                lay_odds = runner_book[0]['runners'][0]['ex']['availableToLay'][0]['price']

                market_odds.append({
                    'back_bet': back_bet,
                    'lay_odds': lay_odds})

        return market_odds


def get_event_market_catalogue(api_key, session_token, eventId, marketTypeCode):
    print('Betfair: \t\tRetreiving market catalogue for event {}...'.format(
        eventId))

    method = 'listMarketCatalogue'
    data = json.dumps({
        'filter': {
            'eventIds': [eventId],
            'marketTypeCodes': [marketTypeCode]},
        'maxResults': 1000,
        'marketProjection': ['RUNNER_METADATA']})

    return betfair_request(api_key, session_token, method, data)


def get_runner_book(api_key, session_token, marketId, runnerId):
    print(
        'Betfair: \t\t\tRetreiving runner book for runner {} within market {}'
        '...'.format(
            runnerId,
            marketId))

    method = 'listRunnerBook'
    data = json.dumps({
        'marketId': marketId,
        'selectionId': runnerId,
        'priceProjection': {'priceData':['EX_BEST_OFFERS']}})

    return betfair_request(api_key, session_token, method, data)


with open('SECRET-api-keys.json') as json_keys:
    betfair_keys = json.load(json_keys)['betfair']
    json_keys.close()

if __name__ == '__main__':
    try:
        # Get a valid session token by logging into the Betfair API
        session_token = login(
            api_key=betfair_keys['api_key'],
            username=betfair_keys['username'],
            password=betfair_keys['password'])

        # Get event IDs of all future football events
        events = get_football_events(
            api_key=betfair_keys['api_key'],
            session_token=session_token)

        # Use those event IDs to get match odds for all events
        events_with_odds = get_all_match_odds(
            api_key=betfair_keys['api_key'],
            session_token=session_token,
            events=events)

        filehandler = open('betfair-{}.pkl'.format(
            datetime.now().strftime('%Y%m%d')), 'wb')
        pickle.dump(events_with_odds, filehandler)

        print('Betfair: Retreived and saved all information. Now what?')

    except Exception as e:
        print('Betfair: ' + e.__class__.__name__ + ' - ' + str(e))
