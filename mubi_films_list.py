import requests
from bs4 import BeautifulSoup
import google_firestore_connect as gfc


def format_id(data):
    title = data['title'].lower().replace(" ", '_')
    director = data['director'].lower().replace(" ", '_')
    id = title+"_"+director
    return id


def get_movies():
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



def main():
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

if __name__ == '__main__':
    main()