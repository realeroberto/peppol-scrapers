#!/usr/bin/env python

# fetches all news from https://peppol.helger.com/ and converts them to jekyll posts


import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from slugify import slugify


class PeppolNewsPostJekyll(object):
    
    def __init__(self, title, date, contents):
        self._title = title
        self._date = datetime.strptime(date, "%Y-%m-%d")
        self._contents = contents

    @property
    def title(self):
        return self._title

    @property
    def date(self):
        return self._date

    @property
    def contents(self):
        return self._contents

    @property
    def slug(self):
        return slugify(self.date.strftime("%Y-%m-%d") + "-" + self.title)
    
    @property
    def filename(self, ext=".html"):
        return self.slug + ext

    @property
    def header(self):
        header = "---\n"               + \
            "layout: post\n"           + \
            "title: %s\n" % self.title + \
            "date: %s\n" % self.date   + \
            "---\n\n"
        return(header)


class PeppolNewsArchive(object):

    def __init__(self, startdate=None):
        self.__startdate = startdate
        self.__previews = []
        page = requests.get("https://peppol.helger.com/public")
        self.__soup = BeautifulSoup(page.content, 'html.parser')
        news = []

        title = ''
        contents = ''

        p = re.compile('(\d{4}-\d{2}-\d{2}) - (.+)')

        previous = False
        for x in self.__soup.find("div", { "id" : "tabs-news" }).children:
            if x.name == 'h3':
                if previous:
                    post = PeppolNewsPostJekyll(title, date, contents)
                    news.append(post)
                    contents = ''
                m = p.match(x.contents[0])
                date = m[1]
                title = m[2]
                previous = True
            else:
                contents = contents + str(x)
        self.news = news

    def __iter__(self):
        self.__i = 0
        self.__j = 0
        return self

    def __next__(self):
        try:
            news = self.news[self.__i]
        except:
            raise StopIteration
        self.__i += 1
        return news



import sys, getopt

def help():
    print('peppol-news.py -s <startdate>')

def main(argv):
    startdate = None

    try:
        opts, args = getopt.getopt(argv,"hs:",["startdate="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-s", "--startdate"):
            startdate = arg

    if startdate:
        startdate = datetime.fromtimestamp(int(startdate))

    for post in PeppolNewsArchive(startdate):
        print("fetching %s..." % post.title)
        with open(post.filename, 'w') as f:
            f.write(post.header)
            f.write(post.contents)


if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit()

