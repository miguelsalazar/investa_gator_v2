from models import CRUD,Ads,TrainData,KeyWords
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob.classifiers import NaiveBayesClassifier as NBC
from textblob.classifiers import DecisionTreeClassifier as DTC
from textblob import TextBlob

class Investigation():

	def __init__(self, site, language):
		self.site = site
		self.language = language

	def investigate(self, data):
		train_crud = CRUD("sqlite:///database.db", Ads, "ads")
		#getting dummy data from http://www.dummytextgenerator.com/#jump
		dummy_crud = CRUD("sqlite:///database.db", TrainData, "training_data")
		train = train_crud.get_all()
		dummy = dummy_crud.get_all()
		t_docs = [elem.text for elem in train_crud.get_all()] #all documents with trafficking
		train = [(elem.text,"trafficking") for elem in train] + [(elem.text,"not trafficking") for elem in dummy]
		cls = []
		#make use of tdf-idf here
		#add in this example: http://scikit-learn.org/0.11/auto_examples/document_classification_20newsgroups.html
		cls.append(NBC(train))
		cls.append(DTC(train))
		for datum in data:
			for cl in cls:
				if cl.classify(datum["text_body"]) == "trafficking":
					self.save_ads([datum], self.site)
			#so I don't have to eye ball things
			if doc_comparison(datum["text_body"], t_docs) == "trafficking":
				self.save_ads([datum], self.site)
				if self.doc_comparison(datum["text_body"], t_docs) == "trafficking":
					self.save_ads([datum], self.site)

			#so I don't have to eye ball things
			if doc_comparison(datum["text_body"], t_docs) == "trafficking":
				self.save_ads([datum], self.site)

				if self.doc_comparison(datum["text_body"], t_docs) == "trafficking":
					self.save_ads([datum], self.site)

		time.sleep(700) # wait ~ 12 minutes
		self.investigate() #this is an infinite loop, which I am okay with.

	def doc_comparison(self, new_document, doc_list):
		total = 0.0
		for doc in doc_list:
			total += self.consine_similarity(new_document,doc)[1]
		if total/len(doc_list) > 0.5: #play with this
			return "trafficking"
		else:
			return "not trafficking"

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