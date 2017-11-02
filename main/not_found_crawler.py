import numpy as np
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import csv
from ssl import SSLError

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
        self.session_open = False
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
            self.session_open = True
            self.valid = True
            print(str(self) + "connection valid")
        except requests.exceptions.ConnectionError as e:
            print(str(self) + "connection error ")
            print(e)
            self.valid = False
        except SSLError as e:
            print(str(self) + "ssl error")
            print(e)
            self.valid = False

    def do_request(self, query):
        query = {"q": query}
        if self.session is None:
            self.session = self.create_session()
            if not self.valid:
                return None
        try:
            return self.session.get(url, params=query)
        except requests.exceptions.ConnectionError as e:
            print(str(self) + "connection error")
            print(e)
            self.valid = False
            return None
        except SSLError as e:
            print(str(self) + "ssl error")
            print(e)
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
            self.session_open = False
            self.session = None
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
            if crawler.sleep_time <= time.time() and crawler.session_open:
                next_crawler = crawler
                break
            if next_crawler is None:
                next_crawler = crawler
            elif next_crawler.sleep_time > crawler.sleep_time:
                # and next_crawler.sleep_time > time.time()
                next_crawler = crawler
    if next_crawler is None:
        return None
    sleep_time = next_crawler.sleep_time - time.time()
    if sleep_time >= 0:
        print("sleep: " + str(sleep_time))
        # anstatt zu schlafen könnte man invalid crawler testen
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
    try:
        return noodle.select("h3.gs_rt > a")[0].get_text()
    except IndexError:
        return noodle.select("h3.gs_rt")[0].get_text().replace("[ZITATION][C] ", "")


def crawl(crawler, title):
    if crawler is not None:
        r = crawler.crawl(title)
        if r is None:
            return -2
        noodles = get_results(r.text)
        if noodles.__len__() > 1:
            return get_title(noodles[0])
        elif noodles.__len__() == 0:
            if "keine übereinstimmenden Artikel" not in r.text:
                print(str(crawler) + "blocked by google")
                crawler.valid = False
                return -2
            else:
                return -1
        else:
            return get_citation_count(noodles[0])
    return -3


def run():
    crawlers = start_crawler(get_proxies())
    with open("bibcitation.csv", "r", encoding="utf-8") as csvsource:
        with open("bibnotfound.csv", "w", encoding="utf-8") as csvdest:
            reader = csv.DictReader(csvsource)
            fieldnames = ["id", "query", "first_match", "tag"]
            writer = csv.DictWriter(csvdest, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                if row["citation"] == "-1":
                    crawler = get_next_crawler(crawlers)
                    match = crawl(crawler, row["title"])
                    while match == -2:
                        crawler = get_next_crawler(crawlers)
                        match = crawl(crawler, row["title"])
                    if match == -3:
                        print("no valid crawler left, quitting")
                        break
                    csv_dict = {"id": row["id"], "query": row["title"], "first_match": match, "tag": row["tag"]}
                    writer.writerow(csv_dict)
                    print("writing: " + str(csv_dict))


run()
