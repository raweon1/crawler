import csv


class Citations:
    def __init__(self):
        self.cit0 = []
        self.cit_1_10 = []
        self.cit_11_50 = []
        self.cit_51_100 = []
        self.cit_101 = []

    def add_citation(self, citation_count):
        if citation_count == 0:
            self.cit0.append(citation_count)
        elif citation_count > 100:
            self.cit_101.append(citation_count)
        elif citation_count > 50:
            self.cit_51_100.append(citation_count)
        elif citation_count > 10:
            self.cit_11_50.append(citation_count)
        else:
            self.cit_1_10.append(citation_count)

    def get_sum_citation_count(self):
        citation_sum = 0
        for cit in self.cit0:
            citation_sum += cit
        for cit in self.cit_1_10:
            citation_sum += cit
        for cit in self.cit_11_50:
            citation_sum += cit
        for cit in self.cit_51_100:
            citation_sum += cit
        for cit in self.cit_101:
            citation_sum += cit
        return citation_sum

    def get_paper_count(self):
        return self.cit0.__len__() + self.cit_1_10.__len__() + self.cit_11_50.__len__() + self.cit_51_100.__len__() + self.cit_101.__len__()

    def get_average_citation_count(self):
        return self.get_sum_citation_count() / self.get_paper_count()


class PaperPerTag:
    def __init__(self, tag):
        self.tag = tag
        self.count = 0
        self.citations = Citations()

    def add_citation(self, citation_count):
        self.count += 1
        if citation_count >= 0:
            self.citations.add_citation(citation_count)

    def get_average_citation_count_per_found_paper(self):
        return self.citations.get_average_citation_count()

    def get_average_citation_count_per_paper(self):
        return self.citations.get_sum_citation_count() / self.get_paper_count()

    def get_ueberdeckungsgrad(self):
        return self.get_found_paper_count() / self.get_paper_count()

    def get_paper_count(self):
        return self.count

    def get_found_paper_count(self):
        return self.citations.get_paper_count()


def get_found_paper_count(papers_per_tag):
    count = 0
    for obj in papers_per_tag:
        count += obj.get_found_paper_count()
    return count


def get_paper_count(papers_per_tag):
    count = 0
    for obj in papers_per_tag:
        count += obj.get_paper_count()
    return count


def get_average_citation_count_per_found_paper(papers_per_tag):
    citation_count = 0
    for obj in papers_per_tag:
        citation_count += obj.citations.get_sum_citation_count()
    return citation_count / get_found_paper_count(papers_per_tag)


def get_average_citation_count_per_paper(papers_per_tag):
    citation_count = 0
    for obj in papers_per_tag:
        citation_count += obj.citations.get_sum_citation_count()
    return citation_count / get_paper_count(papers_per_tag)


def get_ueberdeckungsgrad(papers_per_tag):
    return get_found_paper_count(papers_per_tag) / get_paper_count(papers_per_tag)


def run():
    list = []
    current = None
    with open("bibcitation.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if current is None or current.tag != row["tag"]:
                current = PaperPerTag(row["tag"])
                list.append(current)
            current.add_citation(int(row["citation"]))
    with open("stats.csv", "w", encoding="utf-8") as csvfile:
        fieldnames = ["tag", "paper_found", "paper_count", "percent", "avg_cit_count_found", "avg_cit_count"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for obj in list:
            tmp = {"tag": obj.tag, "paper_found": obj.get_found_paper_count(), "paper_count": obj.get_paper_count(),
                   "percent": obj.get_ueberdeckungsgrad(),
                   "avg_cit_count_found": obj.get_average_citation_count_per_found_paper(),
                   "avg_cit_count": obj.get_average_citation_count_per_paper()}
            writer.writerow(tmp)
        tmp = {"tag": "all", "paper_found": get_found_paper_count(list), "paper_count": get_paper_count(list),
               "percent": get_ueberdeckungsgrad(list),
               "avg_cit_count_found": get_average_citation_count_per_found_paper(list),
               "avg_cit_count": get_average_citation_count_per_paper(list)}
        writer.writerow(tmp)


run()
