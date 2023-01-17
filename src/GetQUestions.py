import json
import os
import cloudscraper
from lxml import html
from bs4 import BeautifulSoup
ROOT_PATH = "https://www.avvo.com/topics/bankruptcy/advice?utf8=%E2%9C%93&search_topic_advice_search%5Bstate%5D=CA&search_topic_advice_search%5Bcontent_type%5D=question&search_topic_advice_search%5Bpublished_year%5D=:year&page=:page_id"
YEAR_PAGES = {
	"2016": 5,
	"2017": 11,
	"2018": 14,
	"2019": 28,
	"2020": 16,
	"2021": 14
}
class Scrapper:
	def __init__(self):
		self.scraper = cloudscraper.create_scraper()	

	def get_questions(self, doc: str) -> list:
		resp = html.fromstring(doc)
		qs = resp.xpath('//div[@class="card topic-advice-question-card"]//div[@class="col-xs-12 u-margin-top-half"]//a[@class="block-link"]/@href')
		#soup = BeautifulSoup(doc, 'html.parser')
		#qs = soup.find_all('a', class_='block-link')
		#print(len(qs))
		questions = qs
		print("\n\n"+str(qs)+"\n\n")
		return questions

	def create_questions_data_from_url(self):
		data = {}
		hole_data = []
		# download the data from the url
		c = 0
		p = 1
		for year, pages in YEAR_PAGES.items():
			for page_id in range(1, pages+1):
				print(page_id)
				page_name = 'page_'+str(p)
				p += 1
				data[page_name] = []
				url = ROOT_PATH.replace(":page_id", str(page_id)).replace(":year", year)
				
				try:
					r = self.scraper.get(url)
					#r = self.text_analyzer.normalize(r.text,remove_html_tag=True)
					aws = self.get_questions(r.text)
					data[page_name] = aws
				except Exception as e:
					print("!"+e)
				if (c != 0 and c % 100 == 0):
					# save the data
					with open('./data/question_links_'+ str(c) +'.json', 'w') as f:
						json.dump(data, f)
				c += 1
		with open('./data/question_links_hole.json', 'w') as f:
			json.dump(data, f)

# main
if __name__ == "__main__":
	scrapper = Scrapper()
	scrapper.create_questions_data_from_url()