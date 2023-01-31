import os
import json
import csv
import ir_measures
from ir_measures import *


# Dictionary for mapping query name to id
query_to_id = {}
with open(os.path.join("data", "queries_bankruptcy.csv"), newline="") as f:
    for id, tag in csv.reader(f, delimiter=","):
        query_to_id[tag] = id


# Ranking model 1 (Candidate-based)
qrels = ir_measures.read_trec_qrels(os.path.join(os.getcwd(), "data", "labels.qrel"))
candidate_run = []
with open("model_two_expertlevel_ranking.dict") as f:
    for key, value in json.loads(f.read()).items():
        query_id = query_to_id[key]
        for lawyer_id, score in value:
            candidate_run.append(ir_measures.ScoredDoc(query_id, lawyer_id, float(score)))

print("Metrics for Model 1 (Candidate-based):")
print(ir_measures.calc_aggregate([AP, RR, P@1, P@2, P@5], qrels, candidate_run))


# Ranking model 2 (Document-based)
qrels = ir_measures.read_trec_qrels(os.path.join(os.getcwd(), "data", "labels.qrel"))
document_run = []
with open("model_two_doclevel_ranking.dict") as f:
    for key, value in json.loads(f.read()).items():
        query_id = query_to_id[key]
        for lawyer_id, score in value.items():
            document_run.append(ir_measures.ScoredDoc(query_id, lawyer_id, score[0][1]))


print("Metrics for Model 2 (Document-based):")
print(ir_measures.calc_aggregate([AP, RR, P@1, P@2, P@5], qrels, document_run))