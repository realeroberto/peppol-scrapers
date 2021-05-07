#!/usr/bin/env python

# fetches all news from peppol.eu and converts them to jekyll posts


import requests
from datetime import datetime
from bs4 import BeautifulSoup
from slugify import slugify


class PeppolNewsPreview(object):

    def __init__(self, fragment):
        self.__fragment = fragment

    @property
    def date(self):
        fragment = self.__fragment.findNext("div", { "class" : "post-data-container" })
        date = fragment.findNext("span", { "class" : "date" }).text.strip()
        return datetime.strptime(date, "%b %d, %Y")

    @property
    def title(self):
        return self.__fragment.findNext("div", { "class" : "entry-title" }).findNext("h1").text

    @property
    def contents(self):
        pass

    @property
    def url(self):
        fragment = self.__fragment.findNext("div", { "class" : "entry-title" })
        return fragment.findNext("a", href=True)["href"]


class PeppolNewsArchivePage(object):

    def __init__(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        self.__previews = []
        for fragment in soup.findAll("article", { "class" : "post" }):
            self.__previews.append(PeppolNewsPreview(fragment))

    @property
    def previews(self):
        return self.__previews


class PeppolNewsArchive(object):

    def __init__(self, startdate=None):
        self.__startdate = startdate
        self.__previews = []

    def __iter__(self):
        self.__i = 0
        self.__j = 0
        return self

    def __next__(self):
        try:
            preview = self.__previews[self.__i]
        except:
            page = requests.get("http://peppol.eu/all-news/page/%d/" % self.__j)
            if page.status_code == 404:
                raise StopIteration
            self.__j += 1
            soup = BeautifulSoup(page.content, 'html.parser')
            for fragment in soup.findAll("article", { "class" : "post" }):
                self.__previews.append(PeppolNewsPreview(fragment))
            preview = self.__previews[self.__i]
        if self.__startdate and preview.date < self.__startdate:
            raise StopIteration
        self.__i += 1
        return preview


class PeppolNewsPost(object):

    def __init__(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        self.__post = soup.find("div", { "class" : "post-data-container" })
        self.__url = url

    @property
    def date(self):
        date = self.__post.findNext("span", { "class" : "date" }).text.strip()
        return datetime.strptime(date, "%b %d, %Y")

    @property
    def title(self):
        return self.__post.findNext("h2").text

    @property
    def contents(self):
        return str(self.__post.findNext("div", { "class" : "single-content" }))

    @property
    def url(self):
        return self.__url


class PeppolNewsPostJekyll(PeppolNewsPost):
    
    def __init__(self, url):
        super().__init__(url)

    @property
    def date(self):
        return super().date

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

    for preview in PeppolNewsArchive(startdate):
        post = PeppolNewsPostJekyll(preview.url)
        print("fetching %s..." % preview.title)
        with open(post.filename, 'w') as f:
            f.write(post.header)
            f.write(post.contents)


if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit()

