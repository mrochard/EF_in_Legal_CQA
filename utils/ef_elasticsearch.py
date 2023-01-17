#from elasticsearch import helpers
import json
from typing import Callable, Generator

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class EF_ElasticSearch:
    def __init__(self):
        # configure elasticsearch
        config = {"http://localhost": "9200"}
        self.es = Elasticsearch(
            [
                config,
            ],
            timeout=300,
        )
        self.last_scroll_id = None


    def _create_mappings(self):
        # Todo:
        #  Improve mapping by defining separate analyzers for separate fields
        #  More details:
        #  - https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
        return {
            #"dynamic": "true",
            "properties": {
                "content": {
                    "type": "text"
                },
            }
        }

    def _create_settings(self):
        # Todo:
        #  Define your own tokenizers, filters and analyzers here
        #  More details:
        #   - https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-tokenizers.html
        #   - https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-tokenfilters.html
        #   - https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-analyzers.html
        return {
            "analysis": {
            }
        }

    def create_index(self, index_name, recreate=False):
        if self.es.indices.exists(index=index_name):
            if recreate:
                self.es.indices.delete(index=index_name)
            else:
                return
        mappings = self._create_mappings()
        settings = self._create_settings()
        print("creating index, name: ", index_name)
        self.es.indices.create(
            index=index_name, body={'mappings':mappings, 'settings':settings})
        
        print("index created successfully, index name: " + index_name)

    def delete_index(self, name):
        print("deleting index, name: ", name)
        self.es.indices.delete(index=name, ignore=[400, 404])
        print("index deleted successfully, index name: " + name)

    def index(self, documents, index_name, is_bulk=False):

        if is_bulk:
            try:
                # make the bulk call, and get a response
                response = bulk(
                    self.es, documents
                )  # chunk_size=1000, request_timeout=200
                print("\nRESPONSE:", response)
            except Exception as e:
                print("\nERROR:", e)

    def populate_index(
        self,index_name: str, data_path: str, generate: Callable[[str, str], Generator]
        ) -> None:

        bulk(self.es, generate(index_name, data_path), refresh=True)
        result = self.es.search(index=index_name, body={'query':{"match_all": {}}})
        nr_docs = result["hits"]["total"]["value"]

    def search(self, index, body):
        try:
            # make the bulk call, and get a response
            return self.es.search(index=index, body=body)
        except Exception as e:
            print("\nERROR:", e)

    def search_all_with_scorll(self, index, body):
        try:
            there_is_next_page = False

            resp = self.es.search(
                index=index,
                body=body,
                scroll="3m",  # time value for search
            )
            self.last_scroll_id = resp["_scroll_id"]
            if len(resp["hits"]["hits"]) >= 10000:
                there_is_next_page = True
            while there_is_next_page:
                resp_scroll = self.es.scroll(
                    scroll="3m",  # time value for search
                    scroll_id=self.last_scroll_id,
                )
                self.last_scroll_id = resp_scroll["_scroll_id"]
                resp["hits"]["hits"].extend(resp_scroll["hits"]["hits"])
                if len(resp_scroll["hits"]["hits"]) >= 10000:
                    there_is_next_page = True
                else:
                    there_is_next_page = False

            if there_is_next_page == False:
                self.last_scroll_id = None
                return resp
            # if hits is zero then there is no new!
            # return
        except Exception as e:
            print("\nERROR:", e)

    def get_with_id(self, index, id_):
        try:
            # make the bulk call, and get a response
            return self.es.get(index=index, id=id_)
        except Exception as e:
            print("\nERROR:", e)

    def termvectors(self, index, body, id):
        try:
            # make the bulk call, and get a response
            return self.es.termvectors(index=index, body=body, id=id)
        except Exception as e:
            print("\nERROR:", e)

