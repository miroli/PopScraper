#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
import pprint

class PopScraper(object):
	URL = 'http://www.popfakta.se/sv/avancerad-sokning/'
	COOKIE_NAME = 'ASP.NET_SessionId'

	def __init__(self, artist='', year_start='--'):
		self._init_session()
		self._set_payload(year_start)
		self._fetch_results()

	def _init_session(self):
		self.session = requests.Session()
		resp = self.session.get(PopScraper.URL)
		self._set_validation(resp)

	def _set_validation(self, response):
		validation = {}
		soup = bs(response.text)
		validators = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION']

		for validator in validators:
			input_element = soup.find('input', { 'id': validator })
			validation[validator] = input_element['value']

		self.validation = validation

	def _set_payload(self, year_start='--'):
		self.payload = {
			'__EVENTTARGET': '',
			'__EVENTARGUMENT': '',
			'__LASTFOCUS': '',
			'ctl00$ContentPlaceHolder1$tbxSearchAlbum': '',
			'ctl00$ContentPlaceHolder1$tbxSearchArtist': '',
			'ctl00$ContentPlaceHolder1$tbxSearchSkivbolag': '',
			'ctl00$ContentPlaceHolder1$tbxSearchDistributor': '',
			'ctl00$ContentPlaceHolder1$ddlFormat': '0',
			'ctl00$ContentPlaceHolder1$ddlYearStart': year_start,
			'ctl00$ContentPlaceHolder1$tbxSearchNo': '',
			'ctl00$ContentPlaceHolder1$tbxSearchTrack': '',
			'ctl00$ContentPlaceHolder1$tbxSearchStudio': '',
			'ctl00$ContentPlaceHolder1$tbxSearchForlag': '',
			'ctl00$ContentPlaceHolder1$tbxSearchPerson': '',
			'ctl00$ContentPlaceHolder1$ddlYearSlut': '--',
			'ctl00$ContentPlaceHolder1$btnSearch': '',
			'ctl00$tbxOverlaySearch': '',
			'ctl00$tbxOverlaySearchLangId': '',
			'ctl00$ContentPlaceHolder1$ddlGridRows': '20',
			'__VIEWSTATE': self.validation['__VIEWSTATE'],
			'__VIEWSTATEGENERATOR': self.validation['__VIEWSTATEGENERATOR'],
			'__EVENTVALIDATION': self.validation['__EVENTVALIDATION']
		}

	def _fetch_results(self):
		r = self.session.post(PopScraper.URL, data=self.payload,
				headers={'content-type': 'application/x-www-form-urlencoded',
						'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'})

		self._pprint_request(r.request)

		self._set_validation(r)
		self.results = bs(r.text)

	def _fetch_next(self):
		payload = {
			'ctl00$ContentPlaceHolder1$smWebbEdit':'ctl00$ContentPlaceHolder1$upResult|ctl00$ContentPlaceHolder1$gvResult',
			'__EVENTTARGET':'ctl00$ContentPlaceHolder1$gvResult',
			'__EVENTARGUMENT':'Page$2',
			'__LASTFOCUS':'',
			'ctl00$ContentPlaceHolder1$tbxSearchAlbum':'',
			'ctl00$ContentPlaceHolder1$tbxSearchArtist':'',
			'ctl00$ContentPlaceHolder1$tbxSearchSkivbolag':'',
			'ctl00$ContentPlaceHolder1$tbxSearchDistributor':'',
			'ctl00$ContentPlaceHolder1$ddlFormat':'0',
			'ctl00$ContentPlaceHolder1$ddlYearStart':'2006',
			'ctl00$ContentPlaceHolder1$tbxSearchNo':'',
			'ctl00$ContentPlaceHolder1$tbxSearchTrack':'',
			'ctl00$ContentPlaceHolder1$tbxSearchStudio':'',
			'ctl00$ContentPlaceHolder1$tbxSearchForlag':'',
			'ctl00$ContentPlaceHolder1$tbxSearchPerson':'',
			'ctl00$ContentPlaceHolder1$ddlYearSlut':'--',
			'ctl00$ContentPlaceHolder1$ddlGridRows':'20',
			'ctl00$tbxOverlaySearch':'',
			'ctl00$tbxOverlaySearchLangId':'',
			'__VIEWSTATE': self.validation['__VIEWSTATE'],
			'__VIEWSTATEGENERATOR': self.validation['__VIEWSTATEGENERATOR'],
			'__EVENTVALIDATION': self.validation['__EVENTVALIDATION'],
			'__ASYNCPOST':'true'
		}

		headers = {
			'Accept':'*/*',
			'Accept-Encoding':'gzip,deflate',
			'Accept-Language':'sv-SE,sv;q=0.8,en-US;q=0.6,en;q=0.4,it;q=0.2',
			'Cache-Control':'no-cache',
			'Connection':'keep-alive',
			# 'Content-Length':'22730',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'Host':'www.popfakta.se',
			'Origin':'http://www.popfakta.se',
			'Referer':'http://www.popfakta.se/sv/avancerad-sokning/',
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36',
			'X-MicrosoftAjax': 'Delta=true',
			'X-Requested-With':'XMLHttpRequest'
		}

		r = self.session.post(PopScraper.URL, data=payload,
				headers=headers)

		print '\n NEXT REQUEST COMING------>'
		self._pprint_request(r.request)

		soup = bs(r.text).find('tr', class_='resultRow')
		print '\n------> First row from next search result...'
		print soup

	def save_results(self, filename):
		with open(filename, 'w') as f:
			for row in self.results.find_all('tr', class_=['resultRow', 'resultRowAlt']):
				record = ''
				for cell in row.find_all('td'):
					if cell.find('a'):
						record += '"www.popfakta.se%s",' % cell.find('a')['href']
					else:
						record += '"%s",' % cell.text
				f.write('%s\n' % record[:-1].encode('utf-8'))



	def _pprint_request(self, req):
		print '%s %s' % (req.method, req.url)
		for k, v in req.headers.items():
			print '%s: %s' % (k, v)

		print ''

		for param in req.body.split('&'):
			if len(param) > 60:
				print param[0:60].replace('=',': ') + '...'
			else:
				print param.replace('=',': ')

if __name__ == '__main__':
	scraper = PopScraper(year_start='2006')
	scraper.save_results(filename='hakan.csv')
	scraper._fetch_next()