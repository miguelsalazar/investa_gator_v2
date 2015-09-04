#!/usr/bin/env python
import argparse
import importlib
import logging
import os
import sys
from utils import utils
# import investigation

def import_scraper(module):
	package = str(".".join(["scrapers", module]))
	scraper = None
	try:
		scraper = importlib.import_module(package)
	except:
		raise ImportError
	return scraper

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-s', '--site')
	parser.add_argument('-l', '--language')
	parser.add_argument('-p', '--location')
	return parser.parse_args()

def main():
	logging.basicConfig(level=logging.INFO)
	
	args = get_args()
	site = args.site
	language = args.language
	location = args.location

	s = import_scraper(site)
	scraper = s.Scraper(place=location, site=site)
	
	data = scraper.start()
	# print data
	sys.exit(1)
	# i = invegstigation.Investigation(site, language)
	
	# investigation_results = i.investigate(data=data)
	# save_investigation(site, investigation_results)
	

if __name__ == '__main__':
	main()