#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Scrapes the Anumex site to generate human trafficking leads. """

import datetime
import logging
import os
import requests
import re
import sys
import time
from models import CRUD, Ads, TrainData, KeyWords
from urlparse import urlparse
from bs4 import BeautifulSoup

__author__ = "Miguel Salazar"
__credits__ = "Eric Schles"
__license__ = "GPL"
__version__ = "0.1"
__email__ = "miguelsalazarg@gmail.com"

# ToDo: Read the db before scraping so that it only scrape what's needed.
class Scraper:
	# Note: There should be a different scraper for every website, each scraper should save to its own table.	
	def __init__(self, place, site):
		print "Initializing scraper"
		if place:
			self.base_url = self.map_place(place)
		else:
			self.base_url = "http://www.anumex.com/anuncios/amor-amistad/0-505" # Base URL for all states.
		#if investigation:
		#	self.investigation = investigation
		#self.language = language
		self.site = site

	def start(self):
	#def initial_scrape(self):
		print "Starting scraper"
		data = self.scrape(self.base_url)
		# self.save_ads(data)
		return data

	def scrape(self, links=[], ads=True, translator=False):
		print "Scraping ad pages..."
		responses = []
		values = {}
		data = []

		urls = self.generate_pages(self.base_url)
		
		for url in urls:
			print "Scraping URL:", url
			r = requests.get(url)
			soup = BeautifulSoup(r.text, "html.parser")
			soup.encode('utf-8')

			values["title"] = self.get_ad_title(soup)
			# values["phone_numbers"]
			values["text_body"] = self.get_ad_text(soup)
			values["images"] = self.get_ad_images(soup)
			values["link"] = url
			values["posted_at"] = self.get_ad_date(soup)
			values["scraped_at"] = str(datetime.datetime.now())
			values["language"] = "Spanish"  # Being lazy here.
			# values["polarity"]
			# values["translated_body"]
			# values["translated_title"]
			# values["subjectivity"]
			time.sleep(3)

		data.append(values)
		return data

	def generate_pages(self, url):
		"""
		Creates a list of URLs containing ads for further scraping.
		"""
		print "Fetching pages..."
		urls = []
		while True:
			print url
			r = requests.get(url)
			soup = BeautifulSoup(r.text, "html.parser")
			soup.encode('utf-8')

			ad_links = self.get_ad_links(soup)
			for link in ad_links:
				urls.append(link)

			next = soup.find_all("a", { "class": "num_next"})

			if next:
				# Fetches the current page.
				current_page = int(soup.find_all("div", { "class": "num_sel"})[0].text)
				# Generates the link for the next page.
				new_url = str(''.join([url.split("?")[0],"?p=",str(current_page+1)]))
				url = new_url
				time.sleep(3)
			else:
				break
		# Note: List needs to be uniquified.
		return urls

	def map_place(self, place):
		"""
		Maps a Mexican state (as defined in ISO 3166-2) to its Anumex URL.
		"""
		# Note: State should be validated. If it doesn't exist, it should default to country.
		# Note: The scraper should add new places (cities) it finds.
		places = {
			"AGU": "http://aguascalientes.anumex.com/anuncios/amor-amistad/1-505",
			"BCN": "http://baja-california.anumex.com/anuncios/amor-amistad/2-505",
			"BCS": "http://baja-california-sur.anumex.com/anuncios/amor-amistad/3-505",
			"CAM": "http://campeche.anumex.com/anuncios/amor-amistad/4-505",
			"CHP": "http://chiapas.anumex.com/anuncios/amor-amistad/5-505",
			"CHH": "http://chihuahua.anumex.com/anuncios/amor-amistad/6-505",
			"COA": "http://coahuila.anumex.com/anuncios/amor-amistad/7-505",
			"COL": "http://colima.anumex.com/anuncios/amor-amistad/8-505",
			"DIF": "http://df.anumex.com/anuncios/amor-amistad/9-505",
			"DUR": "http://durango.anumex.com/anuncios/amor-amistad/10-505",
			"MEX": "http://estado-de-mexico.anumex.com/anuncios/amor-amistad/11-505",
			"GUA": "http://guanajuato.anumex.com/anuncios/amor-amistad/12-505",
			"GRO": "http://guerrero.anumex.com/anuncios/amor-amistad/13-505",
			"HID": "http://hidalgo.anumex.com/anuncios/amor-amistad/14-505",
			"JAL": "http://jalisco.anumex.com/anuncios/amor-amistad/15-505",
			"MIC": "http://michoacan.anumex.com/anuncios/amor-amistad/16-505",
			"MOR": "http://morelos.anumex.com/anuncios/amor-amistad/17-505",
			"NAY": "http://nayarit.anumex.com/anuncios/amor-amistad/18-505",
			"NLE": "http://nuevo-leon.anumex.com/anuncios/amor-amistad/19-505",
			"OAX": "http://oaxaca.anumex.com/anuncios/amor-amistad/20-505",
			"PUE": "http://puebla.anumex.com/anuncios/amor-amistad/21-505",
			"QTO": "http://queretaro.anumex.com/anuncios/amor-amistad/22-505",
			"ROO": "http://quintana-roo.anumex.com/anuncios/amor-amistad/23-505",
			"SLP": "http://san-luis-potosi.anumex.com/anuncios/amor-amistad/24-505",
			"SIN": "http://sinaloa.anumex.com/anuncios/amor-amistad/25-505",
			"SON": "http://sonora.anumex.com/anuncios/amor-amistad/26-505",
			"TAB": "http://tabasco.anumex.com/anuncios/amor-amistad/27-505",
			"TAM": "http://tamaulipas.anumex.com/anuncios/amor-amistad/28-505",
			"TLA": "http://tlaxcala.anumex.com/anuncios/amor-amistad/29-505",
			"VER": "http://veracruz.anumex.com/anuncios/amor-amistad/30-505",
			"YUC": "http://yucatan.anumex.com/anuncios/amor-amistad/31-505",
			"ZAC": "http://zacatecas.anumex.com/anuncios/amor-amistad/32-505",
		}
		return places[place]

	def get_ad_links(self, soup):
		"""
		Grabs the links to the ads from each page.
		"""
		ad_urls = []
		ad_tags = soup.find_all("div", { "class": "res" })
		for ad_tag in ad_tags:
			ad_urls.append(str(ad_tag.a["href"]))
		return ad_urls


	def get_ad_id(self, soup):
		"""
		Gets the ad id
		"""
		# There are different ways to get the ad id. I'm going for the simplest one.
		disclaimer_tag = str(soup.find_all("div", class_="disclaimer")[0])
		# Nasty function. Double split and coercing as an int. 
		ad_id = int(disclaimer_tag.split(": ")[1].split(".")[0])
		return ad_id

	def get_ad_title(self, soup):
		"""
		Gets the ad title	
		"""
		adtitle_tag = soup.find("div", class_="adtitle")
		ad_title = str(adtitle_tag.text).strip()
		return ad_title

	def get_ad_text(self, soup):
		"""
		Gets the ad text.
		"""
		return soup.pre.text

	def get_ad_images(self, soup):
		"""
		Returns the URLs of the pictures that were used in the ad.
		"""
		pictures = []
		thumb_tags = soup.find_all("div", { "class": "thumb" })
		for tag in thumb_tags:
			# Extracts the source file name from the img tag.
			img_file = tag.a.img["src"].split("/")[2].split("?")[0]
			# Builds the full URL.
			img_url = str('/'.join(['http://www.anumex.com/pictures', img_file]))
			pictures.append(img_url)
		return pictures

	def get_ad_date(self, soup):
		"""
		Gets the date in which the ad was published.
		"""
		date_tag = soup.find_all("b", { "class": "r2" })
		# ToDo: Parse dates (25 ago 2015 20:11)
		date = date_tag[0].text
		return date

	# Not needed as of now.
	def get_location(self, soup):
		"""
		Gets the location of the ad.
		"""
		location = soup.find_all("div", { "class": "adlocation" })
		print location
		return location

	def get_phone():
		# Can't be implemented yet.
		pass

	# Not needed as of now.
	def get_related_ads():
		links = soup.find_all("a")
		for l in links:
			o = urlparse(l["href"])
			#print(o.path)

	def save_ads(self, data, site):
		crud = CRUD("sqlite:///database.db", table=site)
		
		for datum in data:
			ad = Ads()
			ad.title=datum["title"]
			ad.phone_numbers=json.dumps(datum["phone_numbers"])
			ad.text_body=datum["text_body"]
			ad.photos=json.dumps(datum["images"])#change this so I'm saving actual pictures to the database.
			ad.link=datum["link"]
			ad.posted_at = datum["posted_at"]
			ad.scraped_at=datum["scraped_at"]
			ad.language=datum["language"]
			ad.polarity=datum["polarity"]
			ad.translated_body=datum["translated_body"]
			ad.translated_title=datum["translated_title"]
			ad.subjectivity=datum["subjectivity"]
			crud.insert(ad)