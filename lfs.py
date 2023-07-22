import re
from datetime import datetime, timedelta
import csv
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://program.lfs.cz'
PROGRAM_URL = BASE_URL + '/?&alldates=1'


def get_content(url):
    result = requests.get(url)
    return result.content


def get_movie(url):
    soup = BeautifulSoup(get_content(url), "lxml")
    movie = {}
    movie['title'] = get_title(soup)
    movie['description'] = get_description(soup)
    movie['csfd'] = get_csfd(soup)
    movie['imdb'] = get_imdb(soup)
    movie['projections'] = get_projections(soup)
    movie['url'] = url
    return movie


def get_title(soup):
    # <h1 class="fg-detail-title">Galaktický expres 999</h1>
    return soup.find_all("h1", {'class': 'fg-detail-title'})[0].string


def get_description(soup):
    # <div class="fg-detail-description"> Rintaro / Japonsko 1979 / 129 min. / 15 let / Blu-ray </div>
    description = soup.find_all("div", {'class': 'fg-detail-description'})[0].string
    logline = soup.find_all("div", {'class': 'fg-detail-logline'})[0].string
    logline = logline.strip() if logline else ''
    return ' '.join(description.split()) + '\n' + logline


def get_csfd(soup):
    csfd = soup.find_all('input', {'class': 'fg-button-big', 'id': 'btnCsfd'})
    if csfd:
        csfd = csfd[0].next_sibling
        csfd = re.findall(r"'https?://.*csfd\.cz/.*',", str(csfd))
        csfd = csfd[0][1:-2] if csfd else None
    else:
        csfd = None
    return csfd


def get_imdb(soup):
    imdb = soup.find_all('input', {'class': 'fg-button-big', 'id': 'btnImdb'})
    if imdb:
        imdb = imdb[0].next_sibling
        imdb = re.findall(r"'https?://.*imdb\.com/.*',", str(imdb))
        imdb = imdb[0][1:-2] if imdb else None
    else:
        imdb = None
    return imdb


def get_projections(soup):
    projections = soup.find_all(
        'div', {'class': 'fg-detail-screening-item-column fg-detail-screening-item-column-date'})
    prjcs = []
    DAY = timedelta(days=1)
    HOUR = timedelta(hours=1)
    for projection in projections:
        data = list(map(lambda e: ' '.join(e.string.split()), projection.children))
        day_data = re.split(r'\W+', data[1])
        time_data = re.split(r'\W+', data[3])
        if len(time_data) == 2:
            time_data.append(time_data[0])
            time_data.append(time_data[1])
        start_time = datetime(
            year=int(day_data[3]), month=int(day_data[2]), day=int(day_data[1]),
            hour=int(time_data[0]), minute=int(time_data[1])
        )
        end_time = datetime(
            year=int(day_data[3]), month=int(day_data[2]), day=int(day_data[1]),
            hour=int(time_data[2]), minute=int(time_data[3])
        )

        if end_time < start_time:
            end_time = end_time + DAY
        elif end_time == start_time:
            end_time = end_time + HOUR
        prjcs.append({'start_time': start_time, 'end_time': end_time, 'place': 'Uherské Hradiště, ' + data[5]})
    return prjcs


def get_movies():
    soup = BeautifulSoup(get_content(PROGRAM_URL), "lxml")
    projections = soup.find_all('a', href=re.compile(r'/detail/\?film=.*'))
    movies = set()
    for projection in projections:
        movies.add(BASE_URL + projection['href'])
    return list(movies)


def main():
    projections = []
    cnt = 0
    movies = get_movies()
    for movie_url in movies:
        movie = get_movie(movie_url)
        for projection in movie['projections']:
            proj = {}
            proj['Subject'] = movie['title']

            s = projection['start_time']
            #proj['Start Date'] = '{:02d}/{:02d}/{}'.format(s.month, s.day, s.year)
            proj['Start Date'] = '{:02d}/{:02d}/{}'.format(s.day,s.month, s.year)
            proj['Start Time'] = '{}:{:02d}'.format(s.hour, s.minute)
            #proj['Start Time'] = datetime.strptime('{}:{:02d}'.format(s.hour, s.minute), "%H:%M").strftime("%I:%M %p")

            e = projection['end_time']
            #proj['End Date'] = '{:02d}/{:02d}/{}'.format(e.month, e.day, e.year)
            proj['End Date'] = '{:02d}/{:02d}/{}'.format(e.day,e.month, e.year)
            proj['End Time'] = '{}:{:02d}'.format(e.hour, e.minute)
            #proj['End Time'] = datetime.strptime('{}:{:02d}'.format(e.hour, e.minute), "%H:%M").strftime("%I:%M %p")
            proj['All Day Event'] = False

            proj['Description'] = movie['description']
            if movie['csfd']:
                proj['Description'] += '\n' + movie['csfd']
            if movie['imdb']:
                proj['Description'] += '\n' + movie['imdb']
            if movie['url']:
                proj['Description'] += '\n' + movie['url']

            proj['Location'] = projection['place']
            projections.append(proj)
        cnt += 1
        print('Done {}/{}'.format(cnt, len(movies)))

    with open('events.csv', 'w') as csvfile:
        fieldnames = [
            'Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for projection in projections:
            writer.writerow(projection)


if __name__ == "__main__":
    main()
