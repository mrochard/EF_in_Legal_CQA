import json
import os
import cloudscraper
#from ef_text_analyzer import TextAnalyzer
from bs4 import BeautifulSoup
from lxml import html

LAWYER_PATH = './data/lawyerid_to_lawyerurl.json'
QUESTIONS_PATH = './data/question_links_hole.json'
#QUESTIONS_PATH = '../data/q.json'

def get_answers(doc: str) -> dict:
	"""
	Extracts the answers from the html of a question page. Answers are in the form of a list of dictionaries.
	With each dictionary containing the answer text and the answerer author.

	:param html: html of the question page
	:return: list of answers
	"""
	new_answers = {}
	soup = BeautifulSoup(doc, 'html.parser')
	answers = soup.find_all('div', {'class':'qa-answer'})
	# get div with id = qa-subject-display
	post = soup.find('div',{ 'id':'qa-subject-display'})
	#print(post)
	# get the question
	title = post.find('h1').text
	text_question = post.find('div', {'id':'question-body'}).text
	#resp = html.fromstring(doc)
	#answers = resp.xpath('div[@class="card qa-lawyer-card qa-answer qa-bordertop"]//div[@class="js-answer"]')
	#xpath('//*[@class="answer-body is-truncated"]/p')
	#print("--"+len(answers))
	for i in range(0, len(answers)):
		a = {
			'title': title,
			'post': text_question,
		}
		#print(answers[i])
		try:
			#author_id = resp[i].xpath('//div[@class="row answer-professional"]//a[@class="lawyer-headshot"]/@href').strip().split('-')[-1].replace('.html','')
			author_id = answers[i].find('div', class_='row answer-professional').find('a', class_='lawyer-headshot').get('href').strip().split('-')[-1].replace('.html','')
		except:
			print("error")
			#print(resp[i].xpath('//div[@class="row answer-professional"]//a[@class="small gtm-subcontext"]/@href'))
		if not author_id in new_answers:
			new_answers[author_id] = []
		#a['response'] = resp[i].xpath('//div[@class="answer-body is-truncated"]/p').text
		a['response'] = answers[i].find('div', class_='answer-body').find('p').text
		#new_answers[author_id].append(resp[i].xpath('//div[@class="answer-body is-truncated"]/p').text)
		new_answers[author_id].append(a)
		#a['author'] = answer.find('div', class_='answer-professional').find('a').get('href')

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
		#self.text_analyzer = TextAnalyzer()
		#self.scraper = cloudscraper.create_scraper(delay=10, browser='chrome',disableCloudflareV1=False)
		self.scraper = cloudscraper.create_scraper()

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
		with open('./data/lawyer_data.json', 'w') as f:
			json.dump(data, f)

	def create_questions_data_from_url(self):
		data = {}
		# download the data from the url
		c = 0
		for page_id, question_urls in self.questions.items():
			print(page_id)
			i=0
			c +=1
			for question_url in question_urls:
				print(i)
				i+=1
				try:
					r = self.scraper.get("https://www.avvo.com"+question_url)
					#r = self.text_analyzer.normalize(r.text,remove_html_tag=True)
					aws = get_answers(r.text)
					#c += len(aws)
					# merge the data
					for k,v in aws.items():
						if k in data:
							data[k].extend(v)
						else:
							data[k] = v

				except Exception as e:
					print("!"+e)
			#with open('./data/pages/question_data_'+ str(c) +'.json', 'w') as f:
			#	json.dump(data, f)
			
		with open('./data/answers_data.json', 'w') as f:
			json.dump(data, f)


	def create_data(self):
		#self.create_lawyer_data_from_url()
		self.create_questions_data_from_url()

if __name__ == "__main__":
    preprocessor = Preprocessor()
    preprocessor.create_data()