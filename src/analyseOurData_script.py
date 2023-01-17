import json

#
# 8910 questions have been deleted out off 9942 questions, so only 1032 questions are left aka 10.3% of the questions
#
if __name__ == "__main__":
	out_data = json.load(open('./data/lawyer_answers_data.json', 'r'))
	
	our_lawyers = list(out_data.keys())
	i=0
	for k in our_lawyers:
		i += len(out_data[k])
	print("We have gathered "+ str(i) +" answers")
	their_data=json.load(open('./data/lawyerid_to_lawyerurl.json', 'r'))
	their_data = [v for k,v in their_data.items()]
	
	their_lawyers = []
	for lawyer in their_data:
		their_lawyers.append(lawyer.replace("https://www.avvo.com/attorneys/","").replace(".html",""))
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
	


