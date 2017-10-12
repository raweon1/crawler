import numpy as np
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import csv
from ssl import SSLError

#TODO Zitation einschließen? siehe "Admission Control and State-Dependent Routing for Multirate Circuit-Switched Traffic"
#   A Dynamic Bandwidth Allocation Mechanism for Connectionless Traffic on ATM Networks

session_cd = (300, 50)
request_cd = (20, 5)
request_per_session = (10, 2)

ua = UserAgent()
url = "https://scholar.google.de/scholar"


def get_proxies():
    proxies = []
    with open("proxies.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            proxie_dict = {"https": "socks5://{}:{}".format(row["ip"], row["port"])}
            proxies.append(proxie_dict)
    return proxies


class CrawlerTmp:
    def __init__(self, proxie, id):
        self.id = id
        self.valid = True
        self.proxie = proxie
        self.sleep_time = time.time()
        self.requests_left = self.get_requests_for_session()
        self.session = None

    def __str__(self):
        return "Crawler " + str(self.id) + ": "

    def get_requests_for_session(self):
        requests_left = int(np.random.normal(request_per_session[0], request_per_session[1]))
        if requests_left <= 0:
            return self.get_requests_for_session()
        return requests_left

    def create_session(self):
        print(str(self) + "open new session")
        s = requests.session()
        s.proxies = self.proxie
        s.headers = {"User-Agent": ua.random}
        self.test_connection(s)
        return s

    def test_connection(self, session):
        try:
            session.get(url)
            print(str(self) + "connection valid")
        except requests.exceptions.ConnectionError:
            print(str(self) + "connection invalid")
            self.valid = False

    def do_request(self, query):
        query = {"as_vis": 1, "q": query}
        if self.session is None:
            self.session = self.create_session()
            if not self.valid:
                return None
        try:
            return self.session.get(url, params=query)
        except requests.exceptions.ConnectionError:
            print(str(self) + "connection error")
            self.valid = False
            return None
        except SSLError:
            print(str(self) + "ssl error")
            self.valid = False
            return None

    def crawl(self, query):
        print(str(self) + "query: " + query)
        if self.requests_left == 0:
            self.session = self.create_session()
            self.requests_left = self.get_requests_for_session()
        r = self.do_request(query)
        self.requests_left -= 1
        if self.requests_left == 0:
            print(str(self) + "waiting for new session")
            self.sleep_time = time.time() + np.random.normal(session_cd[0], session_cd[1])
        else:
            self.sleep_time = time.time() + np.random.normal(request_cd[0], request_cd[1])
        return r


def start_crawler(proxies):
    crawlers = []
    for proxie in proxies:
        crawlers.append(CrawlerTmp(proxie, crawlers.__len__()))
    return crawlers


def get_next_crawler(crawlers):
    next_crawler = None
    for crawler in crawlers:
        if crawler.valid:
            if next_crawler is None:
                next_crawler = crawler
            elif next_crawler.sleep_time > crawler.sleep_time:
                next_crawler = crawler
            if next_crawler.sleep_time <= time.time():
                break
    if next_crawler is None:
        return None
    sleep_time = next_crawler.sleep_time - time.time()
    if sleep_time >= 0:
        print("sleep: " + str(sleep_time))
        time.sleep(sleep_time)
    return next_crawler


def get_results(html):
    soup = BeautifulSoup(html, "html.parser")
    noodles = []
    for noodle in soup.find_all(class_="gs_r gs_or gs_scl"):
        noodles.append(noodle)
    return noodles


def get_citation_count(noodle):
    tmp = noodle.select(".gs_fl > a:nth-of-type(3)")[0].get_text()
    if "Zitiert von: " in tmp:
        return tmp.replace("Zitiert von: ", "")
    return 0


def get_title(noodle):
    return noodle.select("h3.gs_rt > a")[0].get_text()


# @return : citation count, -1 when not found, -2 crawler was blocked by google, -3 no valid crawler left,
def crawl(crawler, title):
    citation = -3
    if crawler is not None:
        r = crawler.crawl(title)
        if r is None:
            return -2
        noodles = get_results(r.text)
        if noodles.__len__() > 1:
            if get_title(noodles[0]).lower() == title.lower():
                return get_citation_count(noodles[0])
            else:
                return -1
        elif noodles.__len__() == 0:
            if "keine übereinstimmenden Artikel" not in r.text:
                print(str(crawler) + "blocked by google")
                crawler.valid = False
                return -2
            else:
                return -1
        else:
            return get_citation_count(noodles[0])
    return citation


def run():
    crawlers = start_crawler(get_proxies())
    with open("bib.csv", "r", encoding="utf-8") as csvsource:
        with open("bibcitation.csv", "w", encoding="utf-8") as csvdest:
            reader = csv.DictReader(csvsource)
            fieldnames = ["id", "author", "title", "year", "citation", "tag"]
            writer = csv.DictWriter(csvdest, fieldnames=fieldnames)
            writer.writeheader()
            id_ = 0
            for row in reader:
                crawler = get_next_crawler(crawlers)
                citation = crawl(crawler, row["title"])
                while citation == -2:
                    crawler = get_next_crawler(crawlers)
                    citation = crawl(crawler, row["title"])
                if citation == -3:
                    print("no valid crawler left, quitting")
                    break
                csv_dict = {"id": id_, "title": row["title"], "author": row["author"], "year": row["year"], "citation": citation,
                            "tag": row["tag"]}
                id_ += 1
                writer.writerow(csv_dict)
                print("writing: " + str(csv_dict))


run()
