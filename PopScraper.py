#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
import re
import math

class PopScraper(object):
    URL = 'http://www.popfakta.se/sv/avancerad-sokning/'
    COOKIE_NAME = 'ASP.NET_SessionId'
    FAKE_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'

    def __init__(self, filename='results.csv', artist='', year_start='--', year_end='--'):
        self.filename = filename
        self.artist = artist
        self.year_start = year_start
        self.year_end = year_end

        self._init_session()

    def _init_session(self):
        """
        Start a new session and set initial validation parameters.
        """
        self.session = requests.Session()
        resp = self.session.get(PopScraper.URL)
        self._set_validation(resp)

    def _set_validation(self, response):
        """
        Parse out the validation parameters from the HTML response.
        """
        validation = {}
        soup = bs(response.text)
        validators = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION']

        for validator in validators:
            input_element = soup.find('input', { 'id': validator })
            validation[validator] = input_element['value']

        self.validation = validation

    def fetch(self):
        """
        Fetch the first 50 results.
        """
        payload = {
            'ctl00$ContentPlaceHolder1$tbxSearchArtist': self.artist,
            'ctl00$ContentPlaceHolder1$ddlFormat': '0',
            'ctl00$ContentPlaceHolder1$ddlYearStart': self.year_start,
            'ctl00$ContentPlaceHolder1$ddlYearSlut': self.year_end,
            'ctl00$ContentPlaceHolder1$btnSearch': '',
            'ctl00$ContentPlaceHolder1$ddlGridRows': '50',
            '__VIEWSTATE': self.validation['__VIEWSTATE'],
            '__VIEWSTATEGENERATOR': self.validation['__VIEWSTATEGENERATOR'],
            '__EVENTVALIDATION': self.validation['__EVENTVALIDATION']
        }

        r = self.session.post(PopScraper.URL, data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': PopScraper.FAKE_AGENT})

        self._set_validation(r)
        self.results = bs(r.text)
        summary = self.results.find('div', class_='summary')
        self.count = re.search(r'\d+', summary.text).group()
        self._save_results()

    def fetch_all(self):
        """
        Fetch all results.
        """
        self.fetch()

        page = 1
        pages_count = math.ceil(int(self.count) / 50)
        while page <= pages_count:
            page = page + 1
            self._fetch_next(page=page)
            self._save_results()

    def _fetch_next(self, page='2'):
        payload = {
            'ctl00$ContentPlaceHolder1$smWebbEdit':'ctl00$ContentPlaceHolder1$upResult|ctl00$ContentPlaceHolder1$gvResult',
            '__EVENTTARGET':'ctl00$ContentPlaceHolder1$gvResult',
            '__EVENTARGUMENT':'Page$%s' % page,
            'ctl00$ContentPlaceHolder1$tbxSearchArtist': self.artist,
            'ctl00$ContentPlaceHolder1$ddlFormat':'0',
            'ctl00$ContentPlaceHolder1$ddlYearStart': self.year_start,
            'ctl00$ContentPlaceHolder1$ddlYearSlut': self.year_end,
            'ctl00$ContentPlaceHolder1$ddlGridRows':'50',
            '__VIEWSTATE': self.validation['__VIEWSTATE'],
            '__VIEWSTATEGENERATOR': self.validation['__VIEWSTATEGENERATOR'],
            '__EVENTVALIDATION': self.validation['__EVENTVALIDATION']
        }

        r = self.session.post(PopScraper.URL, data=payload,
                headers={'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                        'User-Agent': PopScraper.FAKE_AGENT})

        self.results = bs(r.text)
        self._set_validation(r)

    def _save_results(self):
        """
        Write the results to file.
        """
        with open(self.filename, 'a+') as f:
            for row in self.results.find_all('tr', class_=['resultRow', 'resultRowAlt']):
                record = ''
                for cell in row.find_all('td'):
                    if cell.find('a'):
                        record += '"www.popfakta.se%s",' % cell.find('a')['href']
                    else:
                        record += '"%s",' % cell.text
                f.write('%s\n' % record[:-1].encode('utf-8'))


if __name__ == '__main__':
    # Example usage
    scraper = PopScraper(year_start='2007')
    scraper.fetch_all()
