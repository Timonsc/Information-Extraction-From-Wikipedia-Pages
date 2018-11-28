import sys
from nltk import ne_chunk,extract_rels
import nltk
import string
from nltk.tokenize.moses import MosesDetokenizer
import datefinder
import os
import time 
import re
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('maxent_ne_chunker')
#nltk.download('wordnet')
#get_ipython().system('pip install sparqlwrapper')
#get_ipython().system('pip install datefinder')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')

def analyzeEntities(entities): #(file with the url links to wikipedia pages, file with the text from the wikipedia page)
	allNames = [] #["David Bailey"]
	nameUrl = {}
	twoNameParts = [] #['David', 'Bailey']
	nameParts = [] #[['David', 'Bailey'], ['Catherine', 'Deneuve'], etc.]
	namePartsUrl = {}

	for url in entities:
		line = url.rsplit('/', 1)[-1].replace("_", " ").split("(")[0].strip("\n").rstrip() 
		#split the url at /'s and take the -1 part, replace _ with a whitespace, remove everything after the (, remove the \n, remove space at end of string
		url = url.strip("\n")
		

		#Catherine Deneuve
		splitName = line.split(" ")

		twoNameParts=[line.split(" ")[0],line.split(" ")[-1]] #["Cathering","Deneuve"]
		nameParts.append(splitName) #[["Catherine","Deneuve"],["David","Bailey"], etc.]
		for part in splitName:

			namePartsUrl[part] = url
		allNames.append(line)

		nameUrl[line] = url #creates a dictionary that contains all entity names as keys and the corresponding wikipedia page as value 
	#print(nameUrl["Kyoto"],namePartsUrl["Kyoto"],nameParts)
	return nameUrl,namePartsUrl,nameParts




def createAnnotations(allNamesParts,wikiPage,allNames,nameParts,subject,dateTripleFile,typeTripleFile,relationTripleFile): #(file with the text from the wikipedia page, array with all entities with its links (nameUrl variable from analyzeEntities))
	wiki_text = wikiPage.read()
	
	tokenized_text = nltk.word_tokenize(wiki_text)
	index = 0
	dateTriples = []
	types=[]

	def relationFinder(wiki_text, subject,allNames,typeTripleFile,relationTripleFile):
		newText = re.sub("[\(].*?[\)]", "", wiki_text)
		sentences = newText.split(".")
		
		matched_names_array = []
		relations = ["marriage","ex-boyfriend","ex-girlfriend","sister","brother","husband","wife","married"]
		
		for all_sentence in sentences:
			matched_names = []
			all_sentence_words = nltk.word_tokenize(all_sentence)
			all_sentence_words_tagged = nltk.pos_tag(all_sentence_words)
			#print(all_sentence)
			i=0

			for word in all_sentence_words_tagged:
				if word[1] =="NNP":
					second_subject = word[0]
					if all_sentence_words_tagged[i-1][1]=="NNP":
						#print(all_sentence_words_tagged[i-1],all_sentence_words_tagged[i])
						second_subject = all_sentence_words_tagged[i-1][0] + " " + second_subject
						try:
							del matched_names[-1]
						except:
							Incorrect = True
						matched_names.append(second_subject)
					#print(second_subject)
					else:
						matched_names.append(second_subject)	
					
				for item in relations: 
					if item == word[0]:
						#print(all_sentence)
						matched_names.append(item)
				i += 1
			matched_names_array.append(matched_names)
				
		#print(matched_names)
		
		for array in matched_names_array:
			
			q=0
			for word in array:
				#print(word)
				for relation in relations:
					if relation == word:
						try:
							try:
								b = allNames[array[q+1]]
							except:
								b = array[q+1]

							relationTripleFile.write('<"'+allNames[subject]+'","'+relation+'","'+b+'">'+"\n")
							#print(subject,relation,b)
						except:
							Incorrect = True
				q+=1
						
		
		for sentence in sentences[:3]: #first 3 sentences 
			index = 0
			sentence_words = nltk.word_tokenize(sentence)
			sentence_words_tagged = nltk.pos_tag(sentence_words)

			for word in sentence_words_tagged:
				if(word[0] == "is" or word[0] == "was"):
					found_nn = []
					if(sentence_words_tagged[index+1][0] == "a" or sentence_words_tagged[index+1][0] == "an" or sentence_words_tagged[index+1][0] == "the"): 
						i = index
						
						while(i < len(sentence_words_tagged)):
							if (sentence_words_tagged[i][1] =="NN" or sentence_words_tagged[i][1] =="NNP" or sentence_words_tagged[i][1] =="VBG" or sentence_words_tagged[i][1] =="JJ" or sentence_words_tagged[i][1]==","or sentence_words_tagged[i][1]=="CC"):
								found_nn.append(sentence_words_tagged[i][0])
							if (sentence_words_tagged[i][1] =="IN" or sentence_words_tagged[i][1] =="WP"):
								print(sentence_words_tagged[i])
								break
							i +=1
						q = 0
						string=""
						for nn in found_nn:
							if(nn != "," and nn != "and"):
								string = string+" "+nn
							else:
								types.append(string.lstrip())
								string = ""
						print(sentence)
						print(found_nn)
						types.append(string.lstrip())	
				index += 1
		
		for item in types:
			typeTripleFile.write('<"'+allNames[subject]+'","type","'+item+'">'+"\n")
	
	
	relationFinder(wiki_text,subject,allNames,typeTripleFile,relationTripleFile)

	def bornDateFinder(wikiPage):
		wikiPage = wikiPage.split("\n")[0]
		matches = datefinder.find_dates(wikiPage)
		mm = [m.strftime("%Y-%m-%d") for m in matches]
		if len(mm) > 0:
			return mm[0]
		else:
			return "None"
	
	birthDate = bornDateFinder(wiki_text)
	
	monthDayToday = str(time.strftime("%m")) + "-" + str(time.strftime("%d"))
	if birthDate[5:] == monthDayToday:
		birthDate = birthDate[:4]
	dateTriples.append('<"'+allNames[subject]+'","hasDate","'+birthDate+'">')
	dateTripleFile.write(dateTriples[0]+"\n")
	
	#print(tokenized_text)
	for token in tokenized_text:
		for i in nameParts:
			if token == i[-1]: #match last name
				#print(token,i,len(i))
				new_name = i[-1]
				if len(i)!=1:
					for z in range(1,len(i)):
						if token == i[-z] and tokenized_text[index-z] == i[-z-1]: #match last name and one or multiple names beforethe last name
							#print("i'm here")
							new_name = i[-z-1]+" "+new_name
							#print(new_name)
							tokenized_text.pop(index)
							tokenized_text[index-1] = "<entity name='"+allNames[new_name]+'">'+new_name+"</entity>"
							#print("successful encaptulation")
							completeName = True
						else:
							completeName = False
							if new_name == subject:
								tokenized_text[index] = "<entity name='"+allNamesParts[new_name]+'">'+new_name+"</entity>"
								
				if len(i)==1:
					#print(new_name)
					tokenized_text[index] = "<entity name='"+allNames[new_name]+'">'+new_name+"</entity>"
					completeName = True
				
				
		if token.lower() == "she" or token.lower() == "he":
			if completeName == True: 
				#print(new_name,completeName)
				tokenized_text[index-1] = "<entity name='"+allNames[new_name]+'">'+new_name+"</entity>"
			if completeName == False and new_name == subject: 
				tokenized_text[index] = "<entity name='"+allNamesParts[new_name]+'">'+new_name+"</entity>"
		index += 1	
				
						
	backToText = MosesDetokenizer().detokenize(tokenized_text, return_str=True)		
	return backToText			



def main():
	entity_file = open(sys.argv[1]) #entity_list.txt
	wiki_location = sys.argv[2]#location of Wikipedia_corpus /media/sf_Ubuntu-shared/webscience/Wikipedia_corpus
	dateTripleFile = open("dateTriples.txt","w") 
	typeTripleFile = open("typeTriples.txt","w")
	relationTripleFile = open("relationTriples.txt","w")
	

	allNamesUrl,allNamesPartsUrl,nameParts = analyzeEntities(entity_file)
	
	for root, dirs, filenames in os.walk(wiki_location):
		for filename in filenames:
			fullpath = os.path.join(wiki_location, filename)
			wiki_file = open(fullpath, 'r')
			fileName = wiki_file.name.rsplit('/', 1)[-1].split('.')[0].replace("_"," ")
			subject = fileName
			newText = createAnnotations(allNamesPartsUrl,wiki_file,allNamesUrl,nameParts,subject,dateTripleFile,typeTripleFile,relationTripleFile)
			newTextFile = open("newText "+subject+".txt","w")
			newTextFile.write(newText)


if __name__ == '__main__':
	main()