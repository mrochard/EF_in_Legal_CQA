
from ef_elasticsearch import EF_ElasticSearch
from typing import Callable, Generator
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

DOCUMENT_LEVEL_INDEX = "ef_legal_doc_level"
CANDIDATE_LEVEL_INDEX = "ef_legal_user_level"

DOCUMENT_PATH = "./data/lawyer_answers_data.json"
LAWYER_ID_PATH = "./data/lawyerid_to_lawyerurl.json"


def generate_data_user(index_name: str, data_path: str):
	with open(data_path) as f:
		data = json.load(f)
	
	for lawyer_id, answers in data.items():
		
		content = ''
		aws = []
		for answer in answers:
			content += answer['response']
			a = {
				'question': answer['post'],
				'answer': (answer['response']+"\n"+answer['post']).lower(),
			}
			aws.append(a)
		yield {
			"content": content,
			"all_answers_merged_in_array_content_whitespace_w_punc_lowercase": aws,
			"owner_incremental_id": lawyer_id,
			"_index": index_name,
			"_id": lawyer_id,
		}

def generate_data_doc(index_name: str, data_path: str):
	with open(data_path) as f:
		data = json.load(f)
	i = 0
	for lawyer_id, answers in data.items():
		i += 1
		for answer in answers:
			yield {
			"content": (answer['response']+"\n"+answer['post']),
			"owner_incremental_id": lawyer_id,
			"_index": index_name,
			"_id": i,
		}
		

# main
if __name__ == "__main__":


	es = EF_ElasticSearch()
	es.create_index(CANDIDATE_LEVEL_INDEX, recreate=True)
	es.create_index(DOCUMENT_LEVEL_INDEX, recreate=True)
	# Index the data
	es.populate_index(CANDIDATE_LEVEL_INDEX, DOCUMENT_PATH, generate_data_user)
	es.populate_index(DOCUMENT_LEVEL_INDEX, DOCUMENT_PATH, generate_data_doc)
	print("Done")
