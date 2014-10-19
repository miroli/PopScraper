#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
import json

URL = 'http://www.popfakta.se/sv/avancerad-sokning/'
RESULT_FILE = 'results.csv'

def extract_validation():
	"""
	Makes an initial request and extracts the contents from
	the hidden form input fields. Returns dict.
	"""
	validation = {}
	r = requests.get(URL)
	soup = bs(r.text)

	viewstate = soup.find('input', { 'id': '__VIEWSTATE' })
	validation['__VIEWSTATE'] = viewstate['value']

	viewstategenerator = soup.find('input', { 'id': '__VIEWSTATEGENERATOR' })
	validation['__VIEWSTATEGENERATOR'] = viewstategenerator['value']

	eventvalidation = soup.find('input', { 'id': '__EVENTVALIDATION' })
	validation['__EVENTVALIDATION'] = eventvalidation['value']

	validation['cookie'] = r.cookies['ASP.NET_SessionId']

	return validation

def get_results(validation, artist='', album='', year_start='--', year_end='--', page=''):
	"""
	Sends a valid POST request and returns a BeautifulSoup object containing the results.

	@validation: Dict with appropriate form data and ASP session cookie.
	"""
	if page: page = 'Page$%s' % page

	payload = {
		'__EVENTTARGET': 'ctl00$ContentPlaceHolder1$gvResult',
		'__EVENTARGUMENT': page,
		'__LASTFOCUS': '',
		'ctl00$ContentPlaceHolder1$tbxSearchAlbum': album,
		'ctl00$ContentPlaceHolder1$tbxSearchArtist': artist,
		'ctl00$ContentPlaceHolder1$tbxSearchSkivbolag': '',
		'ctl00$ContentPlaceHolder1$tbxSearchDistributor': '',
		'ctl00$ContentPlaceHolder1$ddlFormat': 0,
		'ctl00$ContentPlaceHolder1$ddlYearStart': year_start,
		'ctl00$ContentPlaceHolder1$tbxSearchNo': '',
		'ctl00$ContentPlaceHolder1$tbxSearchTrack': '',
		'ctl00$ContentPlaceHolder1$tbxSearchStudio': '',
		'ctl00$ContentPlaceHolder1$tbxSearchForlag': '',
		'ctl00$ContentPlaceHolder1$tbxSearchPerson': '',
		'ctl00$ContentPlaceHolder1$ddlYearSlut': year_end,
		'ctl00$ContentPlaceHolder1$btnSearch': '',
		'ctl00$tbxOverlaySearch': '',
		'ctl00$tbxOverlaySearchLangId': '',
		'ctl00$ContentPlaceHolder1$ddlGridRows': 50,
		'__VIEWSTATE': validation['__VIEWSTATE'],
		'__VIEWSTATEGENERATOR': validation['__VIEWSTATEGENERATOR'],
		'__EVENTVALIDATION': validation['__EVENTVALIDATION']
	}

	r = requests.post(URL, data=payload, cookies={'ASP.NET_SessionId': validation['cookie']}, headers={'content-type': 'application/x-www-form-urlencoded'})

	soup = bs(r.text)
	results = soup.find('div', {'id': 'ctl00_ContentPlaceHolder1_upResult'})

	return results

def write_results(results):
	"""
	Writes the result in CSV format to RESULT_FILE.

	@results: A BeautifulSoup object with the result div container.
	"""
	with open(RESULT_FILE, 'w') as f:
		for row in results.find_all('tr', class_=['resultRow', 'resultRowAlt']):
			record = ''
			for cell in row.find_all('td'):
				if cell.find('a'):
					record += '"www.popfakta.se%s",' % cell.find('a')['href']
				else:
					record += '"%s",' % cell.text
			f.write('%s\n' % record[:-1].encode('utf-8'))

if __name__ == '__main__':
	validation = extract_validation()
	search_results = get_results(validation, year_start='2010', page='2')
	write_results(search_results)

