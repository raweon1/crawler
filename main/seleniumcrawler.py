from selenium import webdriver
import requests
import csv
import time
from bs4 import BeautifulSoup


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


browser = webdriver.Firefox(webdriver.FirefoxProfile("/Users/game/AppData/Roaming/Mozilla/Firefox/Profiles/2ywvxkz6.default"))

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
            r = requests.__url__(url, params=query)
            print(r.url)
            noodles = get_results(r.text)
            if noodles.__len__() > 1:
                citation = -1
            elif noodles.__len__() == 0:
                print("we got a problem")
                #print(r.text)
                citation = -2
            else:
                citation = get_citation_count(noodles[0])

            csv_dict = {"id": id_, "title": row["title"], "author": row["author"], "year": row["year"], "citation": citation,
                        "tag": row["tag"]}
            id_ += 1
            writer.writerow(csv_dict)
            print("sleep : ", csv_dict)
            time.sleep(5)

browser.get("https://scholar.google.de/")
print(browser.page_source)
time.sleep(10)
