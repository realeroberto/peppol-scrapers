#!/usr/bin/env python

# script to scrape news from peppol.eu

import requests
from datetime import datetime
from bs4 import BeautifulSoup
from slugify import slugify


class PeppolNews(object):

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


class PeppolNewsJekyll(PeppolNews):
    
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



news = PeppolNewsJekyll('http://peppol.eu/2021-call-candidates-openpeppol-elections/')

with open(news.filename, 'w') as f:
    f.write(news.header)
    f.write(news.contents)

