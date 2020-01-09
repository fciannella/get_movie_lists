from requests_html import HTMLSession
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from utils import getLogger
import re
import requests
import pickle
from tqdm import tqdm


import pymongo
mongodb_url = 'mongodb://127.0.0.1:27017'
mongodb_database = 'movies'
client = pymongo.MongoClient(mongodb_url)
database = client[mongodb_database]
collection = database['criterion_lists']

logger = getLogger()

url_list = "https://www.criterion.com/current/top-10-lists"
browser = webdriver.Chrome()

def get_list_with_selenium(url_):

    # browser.get("https://www.zagat.com/m/new-york-city/latest/")
    browser.get(url_)
    time.sleep(1)

    elem = browser.find_element_by_xpath("//button[contains(text(),'Load More')]")

    still_more = True

    j = 0
    while still_more:
        try:
            elem.click()
            j += 1
            time.sleep(2)
        except Exception as e:
            still_more = False
            logger.info("No more %s" % e)

    logger.info("Found %d pages" % j)

    page_html = browser.page_source

    return page_html

def get_data_from_lists(page_source):
    url_soup = BeautifulSoup(page_source)
    entries = url_soup.find_all("div", {'class': "more-container"})
    authors_dict = {}

    for entry in entries:
        link = entry.find('a')['href']
        h5_director_list = entry.find_all('h5')

        for h5 in h5_director_list:
            if h5.has_attr('data-clamp-lines'):
                directors_name_ = h5.text
                try:
                    directors_name = re.match((r'^(.*)[’|\']s Top [10| Ten].*$'), directors_name_).group(1).strip('< \u200b')
                    # directors_name = re.match((r'[^<|^](.*)[’|\']s Top [10| Ten].*$'), directors_name_).group(1)
                    authors_dict[directors_name] = link
                except Exception as e:
                    logger.info("Could not find match for h5: %s. This is the exception: %s" % (h5, e))
    return authors_dict

def get_list_from_link(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, features="lxml")
    film_titles = [ t.text for t in soup.find_all(re.compile(r'h[0-9]+'), {"class": "editorial-film-listitem__title"})]
    film_directors = [d.text for d in soup.find_all(re.compile(r'h[0-9]+'), {"class":"editorial-film-listitem__director tussock"})]
    film_description = [des.text for des in soup.find_all("div", {"class":"editorial-film-listitem__desc"})]
    movies_list = []
    for t,d,des in zip(film_titles, film_directors, film_description):
        movies_list.append({'title': t, 'director': d, 'description': des})
    return movies_list


def main():
    # lists_html= get_list_with_selenium("https://www.criterion.com/current/top-10-lists")
    # authors_dict = get_data_from_lists(lists_html)
    # with open("authors.pkl", "wb") as f:
    #     pickle.dump(authors_dict, f)

    with open("authors.pkl", "rb") as f:
        authors_dict = pickle.load(f)

    movies_dict = {}
    for author, url in tqdm(authors_dict.items()):
        logger.info("Getting author: %s" % author)
        movies_list = get_list_from_link(url)
        logger.info("Got %d entries for author %s" % (len(movies_list), author))
        movies_dict[author] = {"url" : url, "movies_list" : movies_list}
        collection.insert_one({"author": author, "url" : url, "movies_list" : movies_list})
    print(1)

    # url = "https://www.criterion.com/current/top-10-lists/27-steve-buscemi-s-top-10"
    # movies_list = get_list_from_link(url)
    # print(1)

if __name__ == '__main__':
    main()
