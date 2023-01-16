from ef_elasticsearch import EF_ElasticSearch
import json

DOCUMENT_LEVEL_INDEX = "ef_legal_doc_level"
CANDIDATE_LEVEL_INDEX = "ef_legal_user_level"

es = EF_ElasticSearch()


# Read the data
lawyer_path = 'data/lawyer_data.json'
lawyer = json.load(open(lawyer_path, 'r'))

question_path = 'data/question_data.json'
question = json.load(open(question_path, 'r'))

# Index the data
for lawyer_id, lawyer_url in lawyer.items():
	es.create_index(CANDIDATE_LEVEL_INDEX, { "mapping": {"properties": {"content": {"type": "text"}}}})
	es.create_index(DOCUMENT_LEVEL_INDEX, { "mapping": {"properties": {"content": {"type": "text"}}}})

	# Index the data
	es.index(CANDIDATE_LEVEL_INDEX, lawyer_id, {"content": lawyer_url})
