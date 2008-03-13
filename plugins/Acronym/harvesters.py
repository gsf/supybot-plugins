"""
harvesters.py

Created by Michael B. Klein on 2008-03-13.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import urllib2
from BeautifulSoup import BeautifulSoup, SoupStrainer

class AcronymAttic():
	def usage(self):
		return "<term> [~<known_component>...]"
		
	def lookup(self,terms):
		# We could do a full entity encode, but really we just need to 
		# encode spaces and ampersands
		search_string = terms.replace(' ','%20').replace('&','%26')
		url = "http://www.acronymattic.com/results.aspx?q=" + search_string;
		print url
		response = urllib2.urlopen(url)
		strainer = SoupStrainer('table',{ 'id' : 'dgResults' })
		soup = BeautifulSoup(response, parseOnlyThese=strainer, convertEntities=BeautifulSoup.ALL_ENTITIES)
		rows = soup.findAll('tr')[1:]
		results = []
		for tr in rows:
			text = tr.findAll('td',text=lambda(x): len(x) > 1,limit=1)[0]
			results.append(text)
		return results

class AcronymServer():
	def usage(self):
		return "<term>"

	def lookup(self,terms):
		# We could do a full entity encode, but really we just need to 
		# encode spaces and ampersands
		search_string = terms.replace(' ','+').replace('&','&amp;')
	
		url = "http://silmaril.ie/cgi-bin/uncgi/acronyms"
		data = "acronym=Acronym+search&andor=or&terms=" + search_string
		response = urllib2.urlopen(url,data)
		strainer = SoupStrainer('dd')
		soup = BeautifulSoup(response, parseOnlyThese=strainer, convertEntities=BeautifulSoup.ALL_ENTITIES)
		results = []
		for dd in soup.contents:
			text = ''.join(dd.findAll(text=True)).replace(u'\n','')
			results.append(text)
		return results

