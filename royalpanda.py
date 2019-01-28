from bs4 import BeautifulSoup
import pandas as pd
import requests

def soup_from_file(file_path):
    with open(file_path) as open_file:
        return BeautifulSoup(open_file, 'html.parser')


def soup_from_website(url):
    r = requests.get(url)

    if r.status_code == 200:
        return BeautifulSoup(r.text, 'html.parser')
    else:
        raise ConnectionError(
            'Something went wrong trying to access {}'.format(url))


if __name__ == '__main__':
    # TODO Doesn't work, maybe Royal Panda isn't scrapable...
    data = []

    get_soup_from = 'website'

    if get_soup_from == 'file':
        html_file = 'royalpanda-20190124.html'
        soup = soup_from_file(html_file)
    elif get_soup_from == 'website':
        website = 'https://betting.royalpanda.com/#/livecalendar/'
        soup = soup_from_website(website)
    else:
        raise ValueError('What are you trying to do, exactly?')

    # Get the div that contains all data from the saved HTML file
    table_rows = soup.find(
        'div',
        {'class': 'live-calendar-16-scroll-fix-j'}).find_all('ul')

    for row in table_rows:
        if 'filter-j' in row.attrs['class']:
            # The first ul within this div is the header row
            header_text = list(
                map(
                    BeautifulSoup.get_text,
                    row.find_all('div', {'class': 'ellipsis-text'})))
            data.append(header_text)
        else:
            # All subsequent uls are data rows
            row_data = row.text
            data.append(row_data)

    df = pd.DataFrame(data)

    print('Read Royal Panda odds. Now what?')
