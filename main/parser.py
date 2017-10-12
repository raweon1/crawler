import requests
from bs4 import BeautifulSoup
import csv
import time
import numpy as np
from fake_useragent import UserAgent


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

#as_vis=0/1 (0=+zitate)
def tmp():
    proxies = {
        'http': 'socks5://66.187.35.33:22213',
        'https': 'socks5://66.187.35.33:22213',
    }
    ua = UserAgent()
    with open("bib.csv", "r", encoding="utf-8") as csvsource:
        with open("bibcitation.csv", "w", encoding="utf-8") as csvdest:
            reader = csv.DictReader(csvsource)
            fieldnames = ["id", "author", "title", "year", "citation", "tag"]
            writer = csv.DictWriter(csvdest, fieldnames=fieldnames)
            writer.writeheader()
            id_ = 0
            for row in reader:
                query = {"q": row["title"]}
                url = "https://scholar.google.de/scholar"
                headers = {
                    'User-Agent': ua.random}
                r = requests.get(url, params=query, headers=headers, proxies=proxies)
                noodles = get_results(r.text)
                if noodles.__len__() > 1:
                    citation = -1
                    print(get_title(noodles[0]))
                elif noodles.__len__() == 0:
                    citation = -2
                    print("captcha time")
                else:
                    citation = get_citation_count(noodles[0])

                csv_dict = {"id": id_, "title": row["title"], "author": row["author"], "year": row["year"], "citation": citation,
                            "tag": row["tag"]}
                id_ += 1
                writer.writerow(csv_dict)
                print("sleep : ", csv_dict)
                time.sleep(np.random.normal(15, 5))


tmp()