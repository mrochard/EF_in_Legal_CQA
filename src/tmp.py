import json

# main
if __name__ == "__main__":
	data = []
	with open('./data/question_data.json', 'r') as f:
		data = json.load(f)
		keys1 = list(data.keys())

		i=0
		for k in keys1:
			i += len(data[k])

		print(i)
		lawyers=json.load(open('./data/lawyerid_to_lawyerurl.json', 'r'))
		lawyers = [v for k,v in lawyers.items()]
		
		keys2 = []
		for lawyer in lawyers:
			keys2.append(lawyer.replace("https://www.avvo.com/attorneys/","").replace(".html",""))
		keys2 = set(keys2)
		keys1 = set(keys1)
		print(str(len(keys1)))
		print(str(len(keys2)))
		missing = keys2 - keys1
		print(str(len(keys1 - keys2)))
		print("missing "+str(len(missing))+" / "+str(len(keys2)))

		

# 2/3 of the gathered lawyers are present in the given db.
# however 3256 out off 3741 lawyers are not present in out db but where present in their db