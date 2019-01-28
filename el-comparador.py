from datetime import datetime
import re

from bs4 import BeautifulSoup
import requests
from tabulate import tabulate


def get_comparador_football_soup(date):
    base_url = 'http://www.elcomparador.com/futbol/'

    html = get_request(base_url + date)

    return BeautifulSoup(html, 'html.parser')


def get_request(url):
    r = requests.get(url)

    if r.status_code == 200:
        return r.text
    else:
        raise ConnectionError(
            'Something went wrong trying to access {}'.format(url))


if __name__ == '__main__':
    try:
        date_str = datetime.now().strftime('%d-%m-%Y')
        selections = []

        soup = get_comparador_football_soup(date_str)
        soup_events = soup.find_all(id='fila_evento')

        for soup_event in soup_events:
            if ('class' in soup_event.attrs):
                if ('fondo_fila_logos' in soup_event.attrs['class']):
                    # Ignore all wrongly ID'd (e.g. table header) tags
                    continue

            teams = soup_event.find_all(class_='equipo')

            event = {
                'Event Date': date_str,
                'Event Time': soup_event.find(class_='hora').get_text(),
                'Event': ' v '.join(map(lambda tag:
                                        tag.get_text(),
                                        teams))}

            for bet in soup_event.find_all(class_='apuesta'):
                bet_row = bet.parent

                for odds_cell in bet_row.find_all(
                    id='celda_cuotas',
                    class_=['impar', 'par']):

                    bet_lookup = {
                        '1': teams[0].get_text(),
                        'X': 'The Draw',
                        '2': teams[1].get_text()}
                    bet_selection = bet_lookup[bet.get_text()]

                    odds = odds_cell.get_text()
                    odds_link = odds_cell.find('a', href=True)

                    if not odds_link:
                        # Ignore all odds cells without a link to a bookmaker
                        continue

                    odds_bookmaker = re.search(
                        '\((.*)\)',
                        odds_link.attrs['href']
                    )[1].split(',')[1].strip('\'')

                    selection = {
                        'Market Type': 'Match Odds',
                        'Selection': bet_selection,
                        'Exchange': '',
                        'Exchange Odds': '',
                        'Exchange Stake': '',
                        'Exchange Promotion': '',
                        'Exchange Winning Commission': '',
                        'Bookmaker': odds_bookmaker,
                        'Bookmaker Odds': odds,
                        'Bookmaker Stake': '',
                        'Bookmaker Promotion': '',
                        'Profit If Bookmaker Bet Wins': '',
                        'Profit If Exchange Bet Wins': '',
                        'Possible Loss': '',
                        'Won Bookmaker Bet': '',
                        'Profit': '',
                        'Note': ''}

                    selections.append(dict(event, **selection))

        print(tabulate(selections))

        print('El Comparador: Got a soup of today\'s odds. Now what?')

    except Exception as e:
        print('El Comparador: ' + e.__class__.__name__ + ' - ' + str(e))
