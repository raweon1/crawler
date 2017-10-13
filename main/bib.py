from main import bibsonomy
import csv

api_key = "9730b1f7dded2c2c42d478eb386f91fe"
username = "raweon"

json_source = bibsonomy.REST(username, api_key)
bib = bibsonomy.BibSonomy(json_source)

resource_type = "publication"
user = "itc"
tags = ["itc01", "itc02", "itc03", "itc04", "itc05", "itc06", "itc07", "itc08", "itc09",
       "itc10", "itc11", "itc12", "itc13", "itc14", "itc15", "itc16", "itc17", "itc18", "itc19",
       "itc20", "itc21", "itc22", "itc23", "itc24", "itc25", "itc26", "itc27", "itc28", "itc29"]
#tags = ["itc20", "itc21", "itc22", "itc23", "itc24", "itc25", "itc26", "itc27", "itc28", "itc29"]

with open("bib.csv", "w", encoding="utf-8") as csvfile:
    fieldnames = ["id", "author", "title", "year", "tag"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    id_ = 0
    for tag in tags:
        posts = bib.getPostsForUser(resource_type, user, [tag])
        for post in posts:
            publication = post.resource
            try:
                csv_dict = {"id": id_, "title": publication.title, "author": publication.author, "year": publication.year,
                            "tag": tag}
                writer.writerow(csv_dict)
                id_ += 1
            except AttributeError:
                pass
