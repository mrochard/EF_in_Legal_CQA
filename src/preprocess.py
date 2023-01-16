import json
import os
import cloudscraper
from ef_text_analyzer import TextAnalyzer
from bs4 import BeautifulSoup

LAWYER_PATH = 'data/lawyerid_to_lawyerurl.json'
#QUESTIONS_PATH = 'data/question_links_bankruptcy.json'
QUESTIONS_PATH = 'data/q.json'

def get_answers(html: str) -> list:
	"""
	Extracts the answers from the html of a question page. Answers are in the form of a list of dictionaries.
	With each dictionary containing the answer text and the answerer author.

	:param html: html of the question page
	:return: list of answers 
	"""
	new_answers = []
	soup = BeautifulSoup(html, 'html.parser')
	answers = soup.find_all('div', class_='qa-answer')
	print(soup)
	for answer in answers:
		a = {}
		a['text'] = answer.find('div', class_='answer-body').find('p').text
		a['author'] = answer.find('div', class_='answer-professional').find('a').get('href')
		a['author'] = a['author'].split('-')[-2]
		new_answers.append(a)
	return new_answers

def get_lawyer_data():
	lawyer_path = LAWYER_PATH
	lawyer = json.load(open(lawyer_path, 'r'))
	return lawyer

def get_questions_data():
	questions_path = QUESTIONS_PATH
	questions = json.load(open(questions_path, 'r'))
	return questions

class Preprocessor:

	def __init__(self):
		self.lawyer = get_lawyer_data()
		self.questions = get_questions_data()
		self.text_analyzer = TextAnalyzer()
		self.scraper = cloudscraper.create_scraper(delay=10, browser='chrome',disableCloudflareV1=False)
	
	def create_lawyer_data_from_url(self):
		data = []
		# download the data from the url
		for lawyer_id, lawyer_url in self.lawyer.items():
			try:
				r = self.scraper.get(lawyer_url)
				#r = self.text_analyzer.normalize(r.text,remove_html_tag=True)
				r = {"content": r}
				data.append(r)
			except Exception as e:
				print("!!"+e)
		# save the data
		with open('data/lawyer_data.json', 'w') as f:
			json.dump(data, f)
	
	def create_questions_data_from_url(self):
		data = []
		# download the data from the url
		for page_id, question_urls in self.questions.items():
			for question_url in question_urls:
				try:
					r = self.scraper.get(question_url)
					#r = self.text_analyzer.normalize(r.text,remove_html_tag=True)
					aws = get_answers(r.text)
					data.extend(aws)
				except Exception as e:
					print("!"+e)
		# save the data
		with open('data/question_data.json', 'w') as f:
			json.dump(data, f)

	def create_data(self):
		#self.create_lawyer_data_from_url()
		self.create_questions_data_from_url()

if __name__ == "__main__":
    preprocessor = Preprocessor()
    preprocessor.create_data()