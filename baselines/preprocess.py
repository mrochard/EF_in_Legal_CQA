from ef_elasticsearch import elasticsearch

es = elasticsearch()
es.create_index("test", {"mappings": {"properties": {"text": {"type": "text"}}}})