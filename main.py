import requests
from bs4 import BeautifulSoup
import google_firestore_connect as gfc
from datetime import datetime, timedelta
import re


def format_id(data):
    title = data['title'].lower().replace(" ", '_')
    director = data['director'].lower().replace(" ", '_')
    id = title+"_"+director
    return id


def get_movies(data, context):
    """

    """
    url = "https://mubi.com/showing"
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, features="lxml")
    articles = soup.find_all("article", {"class": "full-width-tile full-width-tile--now-showing"})

    for article in articles:
        title = article.find("h2").text
        director = article.find("h3").find("span", {"itemprop": "name"}).text
        location_and_year = article.find("h3").find("span", {"class":"now-showing-tile-director-year__year-country light-on-dark"}).text
        text = article.find("p", {"class": "full-width-tile__our-take light-on-dark"}).text
        data = {"title" : title, "director": director, "location_and_year": location_and_year, "text": text.strip()}
        id = format_id(data)
        gfc.add_movie(data, id)
    return True

def get_film_url_and_author_url(a_hrefs):
    author_url = ""
    film_url = ""
    for a in a_hrefs:
        if "cast" in a['href']:
            author_url = "https://mubi.com"+a['href']
        elif "films" in a['href']:
            film_url = "https://mubi.com"+a['href']
        else:
            continue
    return author_url, film_url




def main(data, context):
    url = "https://mubi.com/showing"
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, features="lxml")
    articles = soup.find_all("article", {"class": "full-width-tile full-width-tile--now-showing"})
    rolling_days = 30

    for article in articles:
        title = article.find("h2").text
        director = article.find("h3").find("span", {"itemprop": "name"}).text
        location_and_year = article.find("h3").find("span", {"class":"now-showing-tile-director-year__year-country light-on-dark"}).text
        text = article.find("p", {"class": "full-width-tile__our-take light-on-dark"}).text
        a_hrefs = article.find_all('a', href=True)
        author_url, film_url = get_film_url_and_author_url(a_hrefs)
        days_left = article.find("div", {"class": "full-width-tile__days-left"}).text
        days = re.match(r"^([0-9]+).*", days_left)
        if days:
            num_days = int(days.group(1))
        else:
            num_days = 1
        created = datetime.today() - timedelta(days=rolling_days - num_days)

        data = {"title": title,
                "director": director,
                "location_and_year": location_and_year,
                "text": text.strip(),
                "author_url": author_url,
                "film_url": film_url,
                # "created": gfc.firestore.SERVER_TIMESTAMP
                "created": created
                }

        id = format_id(data)
        gfc.add_movie(data, id)

if __name__ == '__main__':
    main("", "")