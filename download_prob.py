#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup

class ContestParser:
    def __init__(self, html):
        source = BeautifulSoup(html, 'lxml')
        self.source = source



def main():
    url = 'https://codeforces.com/contest/1464'
    source = requests.get(url).text
    contest = ContestParser(source)
    print(contest.source.prettify())







if __name__ == '__main__':
    main()

