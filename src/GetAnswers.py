import json
import os
import cloudscraper
#from ef_text_analyzer import TextAnalyzer
from bs4 import BeautifulSoup
from lxml import html


QUESTIONS_PATH = './data/question_links_bankruptcy.json'

LAWYER_ID_PATH = "./data/lawyerid_to_lawyerurl.json"
DOCUMENT_PATH = "./data/lawyer_answers_data.json"
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
	try:
		post = soup.find('div',{ 'id':'qa-subject-display'}).text.strip()
	except:
		raise Exception("Error: no post found in the page: "+doc)
	#print(post)
	# get the question
	#title = post.find('h1').text
	#text_question = post.find('div', {'id':'question-body'}).text
	#resp = html.fromstring(doc)
	#answers = resp.xpath('div[@class="card qa-lawyer-card qa-answer qa-bordertop"]//div[@class="js-answer"]')
	#xpath('//*[@class="answer-body is-truncated"]/p')
	#print("--"+len(answers))
	for i in range(0, len(answers)):
		a = {
			'post': post,
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
		#a['response'] = resp[i].xpath('//div[@class="answer-body is-truncated"]/p').text answer-upvote-section
		a['response'] = answers[i].find('div', class_='answer-body').find('p').text.strip()
		votes = answers[i].find('span', class_='answer-upvote-section').find_all('span')
		#print(votes)
		a['upvotes'] = int(votes[4].text.replace(' lawyer agrees','').replace(' lawyers agree',''))
		a['helpful'] = int(votes[0].text)
		if len(votes) > 6:
			a['most_helpful'] = "Voted as Most Helpful" in votes[6].text
		else:
			a['most_helpful'] = False
		#new_answers[author_id].append(resp[i].xpath('//div[@class="answer-body is-truncated"]/p').text)
		new_answers[author_id].append(a)
		#a['author'] = answer.find('div', class_='answer-professional').find('a').get('href')

	return new_answers

def get_questions_data():
	questions_path = QUESTIONS_PATH
	questions = json.load(open(questions_path, 'r'))
	return questions

class Preprocessor:

	def __init__(self):
		#self.lawyer = get_lawyer_data()
		self.questions = get_questions_data()
		#self.text_analyzer = TextAnalyzer()
		#self.scraper = cloudscraper.create_scraper(delay=10, browser='chrome',disableCloudflareV1=False)
		self.scraper = cloudscraper.create_scraper()

	def create_questions_data_from_url(self):
		data = {}
		# download the data from the url
		c = 0
		deleted_questions = 0
		for page_id, question_urls in self.questions.items():
			print(page_id)
			i=0
			for question_url in question_urls:
				print(i)
				i+=1
				r = self.scraper.get(question_url)
				#r = self.text_analyzer.normalize(r.text,remove_html_tag=True)
				try:
					aws = get_answers(r.text)
					for k,v in aws.items():
						if k in data:
							data[k].extend(v)
						else:
							data[k] = v
				
				except:
					print("error in page: " + page_id + " question: " + question_url +" the question likely has been deleted")
					deleted_questions +=1
					continue
					#raise Exception("error in page: " + page_id + " question: " + question_url)
				#c += len(aws)
				# merge the data
				c +=1
				#if(c%100==0):
				#	with open('./data/pages/lawyer_answers_data_'+ str(c) +'.json', 'w') as f:
				#		json.dump(data, f)
		
		with open(DOCUMENT_PATH, 'w') as f:
			json.dump(data, f)
		print(str(deleted_questions)+" questions have been deleted out off "+str(c+deleted_questions)+" questions")

	def create_data(self):
		#self.create_lawyer_data_from_url()
		self.create_questions_data_from_url()

if __name__ == "__main__":
	preprocessor = Preprocessor()
	preprocessor.create_data()

	with open(LAWYER_ID_PATH) as f:
		lawyers = json.load(f)
		
		new_lawyers = {}
		for lawyer_id, lawyer_url in lawyers.items():
			avvo_id = lawyer_url.replace("https://www.avvo.com/attorneys/", "").replace(".html", "")
			new_lawyers[avvo_id]=lawyer_id

	with open(DOCUMENT_PATH) as f:
		data = json.load(f)
		new_data = {}
		ids = []
		for avvo_id, answers in data.items():
			new_id = new_lawyers[avvo_id]
			new_data[new_id] = answers
			ids.append(new_id)
		
	with open(DOCUMENT_PATH, "w") as f:
		json.dump(new_data, f)
	with open("./data/lawyerIds.json", "w") as f:
		json.dump(ids, f)
