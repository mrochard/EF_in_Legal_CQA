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
answers_id = 0

def get_answers(doc: str,id:int) -> dict:
	"""
	Extracts the answers from the html of a question page. Answers are in the form of a list of dictionaries.
	With each dictionary containing the answer text and the answerer author.

	:param html: html of the question page
	:return: list of answers
	"""
	global answers_id
	new_answers = {}
	soup = BeautifulSoup(doc, 'html.parser')
	answers = soup.find_all('div', {'class':'qa-answer'})
	# get div with id = qa-subject-display
	try:
		post = soup.find('div',{ 'id':'qa-subject-display'}).text.strip()
	except:
		raise Exception("Error: no post found in the page: "+doc)
	
	for i in range(0, len(answers)):
		a = {
			'post': post,
		}
		try:
			author_id = answers[i].find('div', class_='row answer-professional').find('a', class_='lawyer-headshot').get('href').strip().split('-')[-1].replace('.html','')
		except:
			print("error in author id")
		if not author_id in new_answers:
			new_answers[author_id] = []
		a['response'] = answers[i].find('div', class_='answer-body').find('p').text.strip()
		votes = answers[i].find('span', class_='answer-upvote-section').find_all('span')
		a['upvotes'] = int(votes[4].text.replace(' lawyer agrees','').replace(' lawyers agree',''))
		a['helpful'] = int(votes[0].text)
		a['question_id'] = id
		a['answer_id'] = answers_id
		answers_id += 1
		if len(votes) > 6:
			a['most_helpful'] = "Voted as Most Helpful" in votes[6].text
		else:
			a['most_helpful'] = False

		a['comments'] = []
		try:
			comments = answers[i].find_all('div', {'class':'comment-header'})
			#print(comments)
			for comment in comments:
			#	print(comment)
				c = {
					'author': comment.find('strong').text,
					'text': comment.find('p').text.strip(),
					'is_asker': comment.find('strong').text == 'Asker',
				}

				a['comments'].append(c)
		except:
			a['comments'] = []
		new_answers[author_id].append(a)

	return new_answers

def get_questions_data():
	questions_path = QUESTIONS_PATH
	questions = json.load(open(questions_path, 'r'))
	return questions

class Preprocessor:

	def __init__(self):
		self.questions = get_questions_data()
		self.scraper = cloudscraper.create_scraper()

	def create_questions_data_from_url(self):
		data = {}
		# download the data from the url
		c = 0
		deleted_questions = 0
		q_id = 0
		for page_id, question_urls in self.questions.items():
			print(page_id)
			i=0
			for question_url in question_urls:
				print(i)
				i+=1
				r = self.scraper.get(question_url)
				try:
					aws = get_answers(r.text,q_id)
					for k,v in aws.items():
						if k in data:
							data[k].extend(v)
						else:
							data[k] = v
					q_id += 1
				except:
					print("error in page: " + page_id + " question: " + question_url +" the question likely has been deleted")
					deleted_questions +=1
					continue
				c +=1
		
		with open(DOCUMENT_PATH, 'w') as f:
			json.dump(data, f)
		print(str(deleted_questions)+" questions have been deleted out off "+str(c+deleted_questions)+" questions")

	def create_data(self):
		#self.create_lawyer_data_from_url()
		self.create_questions_data_from_url()

def analyseOurData():

	print("------------------------------------------------------------")
	print("------------------------ Analysis --------------------------")
	print("------------------------------------------------------------")
	out_data = json.load(open(DOCUMENT_PATH, 'r'))
	
	our_lawyers = list(out_data.keys())
	i=0
	for k in our_lawyers:
		i += len(out_data[k])
	print("We have gathered "+ str(i) +" answers")
	their_data=json.load(open(LAWYER_ID_PATH, 'r'))
	#their_data = [v for k,v in their_data.items()]
	
	their_lawyers = their_data.keys()
	their_lawyers = set(their_lawyers)
	our_lawyers = set(our_lawyers)
	print("--------------------")
	print("We have gathered "+str(len(our_lawyers))+" lawyers")
	print("They gathered "+str(len(their_lawyers))+" lawyers")
	print("Or "+str(len(our_lawyers)/len(their_lawyers)*100)+"% of their lawyers")
	missing = their_lawyers - our_lawyers
	print("--------------------")
	print("We are missing "+str(len(missing))+" lawyers in our data out off their "+str(len(their_lawyers))+" lawyers ("+str(len(missing)/len(their_lawyers)*100)+"%)")
	print("We have "+str(len(our_lawyers - their_lawyers))+" lawyers that they don't have")

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
	analyseOurData()