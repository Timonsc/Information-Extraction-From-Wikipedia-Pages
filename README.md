# Information Extraction From Wikipedia Pages
Guo Lei & Timon Schneider
16-02-2018

# Getting Started
These instructions will get you a copy of the project up and running on your local machine for testing purposes.

#### Prerequisites
We developed the program in Python 3.6.4. Apart from the standard Python library we used the Natural Language Toolkit 3.2.5 and the datefinder library. Use the following commands to install the libraries.
```
$ pip3 install nltk
$ pip3 install datefinder
```
Within the Python environment use the following commands to download the needed packages.
```python
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('wordnet')
nltk.download('words')
```

#### How to run
Navigate to folder of wiki.py. Note: we only tested the program in Ubuntu and MacOS.
```
$ python3 wiki.py entity_list.txt [location of the Wikipedia files]
```



## Description
In this code we made our goal to write a compact piece of code that would work for any other Wikipedia files. To secure this goal we made tried to keep the amount of exceptions to an absolute minimum. Meaning that in no cases we used exceptional lines of code for one single, or even a few, cases that gave a result other than what we aimed for. This lead to very sophisticated and compact algorithms that will make some, although very little, mistakes. 

# File description
Brief description of the documents in the file:

* [entity_list.txt] - List of entity url
* [newText-~~~.txt] - The annotated version of the wikipedia text.
* [dateTriples.txt] - Birthdate triple of entity
* [typeTriples.txt] - Type triple of entity
* [relationtriples.txt] - Recognized relations between entities.
### Code architecture
* In __def main()__ we get the input parameters, open the files that we will use to store the triples and the annotated text and extract the subject of the Wikipedia file from the file name. From here we pass on the necessary variables and run the functions. Some only once, others in a for loop for every file in the Wikipedia_corpus folder.
* * __def analyzeEntities()__ extracts the entity names in all necessary data structures.
* * __def createAnnotations()__ contains an algorithm to annotate the text and other functions that have to be executed for every file. 
* * * __def relationFinder()__ finds relations between the different entities and the types of the entity of the Wikipedia page and creates the type triple and relation triple.
* * * __def bornDateFinder()__ finds the most relevant date for the entity and creates the date triple.


## 1. Anotate the entity names in the Wikipedia text files.
We wanted to replace single name parts (e.g. Deneuve) and complete names (Catherine Deneuve). We chose to create two dictionaries, one with the full names as key and the uri as values and one with the name parts as key and the uri as value. Also we created an array in an array with all the name parts for evey entity ([["Catherine","Deneuve"],["David","Bailey"], etc.]).

#### Extract names from the uri's
We use split strip and replace to extract the names from the url.
Create two dictionaries and two arrays. 

'''
allNames = ["Catherine Deneuve","David Bailey" etc.]
allNameParts = [["Catherine","Deneuve"],["David","Bailey"], etc.]
nameUrl = {"Catherine Deneuve": "http://en.wikipedia.org/wiki/Catherine_Deneuve", etc.}
namePartsUrl = {"Catherine": "http://en.wikipedia.org/wiki/Catherine_Deneuve", "Deneuve": "http://en.wikipedia.org/wiki/Catherine_Deneuve", etc.}
'''
#### Create the annotations
We use the dictionaries to match the names with the uri's. We use the arrays match the last name first and then see whether in that case if there are also prenames before the surname. Like this we prevent that double annotations occur for one name.
```
word_tokenize(): # Is used to transform the text into an array of single words.
```
We match all words in the array with the last names in the __allNameParts__ array. Then we check if there are also first names and replace everything with the annotation using one of the dictionaries.
To prevent matching entities with the same surname, we only annotate single surnames if it is the same as the surname of the subject of the Wikipedia file. This still doesn't prevent wrongly matching family members of the subject with a different first name with the subject though. It does help preventing matching unrelated entities in other files.
Then we match "he" and "she" with the words in the array. We create the annotations with the last entity found in the text before the match. We assumed that he and she will only be used for talking about the subject entity. If this wouldn'd be the case the algorithm would look for the last entity that is unrelated. In practice this method gives a very high accuracy.

#### Shortcomings
* Since we tokenized the text we have to put the text back together. To do this we __MosesDetokenizer()__ from the nltk library. Some of the layout was lost and there were some mistakes with whitespaces.
* The algorithm assumes that the wikipedia files do not contain different entities than the subject with the same last name. It will recognize the last name and replace it for a entity of the subject. If the entity list would contain these family members the accuracy of the algorithm would improve.
* We assume the Wikipedia text only speaks in terms of he and she about the subject.


## 2. Find the most important date for the subject entity
```
datefinder(): is usded for finding the dates
```
Born date always appeared at the first date, we just used datefinder to find all the dates and then if the length of the vector is more than one, then we return the first date to be the born date. In the cases of the cities the datefinder only returns the year in which the city is created. This made the datefinder return the month and day of today. To prevent this we check if the returned month and day is the same as the month and day of today. If so, we only return the year.
#### Shortcomings
* If we run the algorithm on the same day of the birth date of one of the person entities, it will return only the year. This could be easily be prevented by building in a boolean of foundDayAndMonth.


## 3. Extract the type of the subject entity
We assumed that the type of the subject will always be in one if the first three sentences. For the files given in this exercise this gave an very high accuracy. In these three sentences match with the words "is" and "was". Then we analyze the following words with NLTK:
```
sentence_words = nltk.word_tokenize(sentence) # Creates an array of the words
sentence_words_tagged = nltk.pos_tag(sentence_words) # Tags the words with the type.
```
After the matches we want to get the store the words with the following types: NN, NNP, VBG, JJ and CC (respectively nouns, verbs, adjectives and coordinating conjunctions). We keep storing those until we find an IN or WP (Preposition or subordinating conjunction or Wh-pronoun) or until the sentence ends. Then per sentence we put them together as one type. This gave us very good results. We can imagine though, that with other texts we might have to take more word types into account make sure the algorithms keeps giving clean results. 
This algorithm recognizes what words should be put together as one type and what words should become their own type.
```
# From "Benjamin Biolay is a French singer, songwriter, musician, actor and record producer" it creates the following types.
<"http://en.wikipedia.org/wiki/Benjamin_Biolay","type","French singer">
<"http://en.wikipedia.org/wiki/Benjamin_Biolay","type","songwriter">
<"http://en.wikipedia.org/wiki/Benjamin_Biolay","type","musician">
<"http://en.wikipedia.org/wiki/Benjamin_Biolay","type","actor">
<"http://en.wikipedia.org/wiki/Benjamin_Biolay","type","record producer">

# For Catherine Deneuve it recognizes the types perfectly.
<"http://en.wikipedia.org/wiki/Catherine_Deneuve","type","French actress">
<"http://en.wikipedia.org/wiki/Catherine_Deneuve","type","twelve-time Cesar Award nominee">
```
#### Shortcomings
* The algorithm that splits the types is not perfect. For example it splits English fashion and portrait photographer into two types; "English fashion" and "portraint photographer".
* Not all word types are considered. More general rules about linguistics could perfectionize the algorithm.

## 4. Find relations 
In this part look for relations between entities, listed in the entity list or not. If it is listed in the entity list, we put the uri in the triple, otherwise we put the matched word/name in the uri. Our method is based upon the following assumptions that gave us quite good results.
* All relations between entities that wil find will be between the subject of the file and another entity of which the subject will appear first.
* All relations that we find will be in the same sentence.
This is how the algorithm works:
1. Split the text up in sentences and split the sentences up in tokenized words ([word],[wordtype])
2. Look in the sentence array for words of the type NNP or "relation words" listed in the predefined relations array and put them alltogether in a new array __matched_names_array__. If multiple NNP's are sequential put them together in one cell.
3. Then in another loop, find the match the "relation words" in the __matched_names_array__ with the following NNP in that array.
4. Create a triple from those items.

```
# The predefined "relation words"
relations=["marriage","ex-boyfriend","ex-girlfriend","sister","brother","husband","wife","married"]
```
### Shortcomings
* The results that this algorithm gives are quite accurate. Though, with the assumptions that we made we might have missed some relations.
* The algorithm has some problems with synomyms. In the Didier Pironi file it mathes "Didier Pironi" and "sister" with "Ferrari" because Didiers teammate drove for the sister team Ferrari.

## Conclusion
We tried to solve the exercises with a very compact and sohpisticated code. Thinking about what piece of code would work for every scenario was most time consuming, much more than actually writing the code, but also very interesting. With minimum exceptions and adaptions to the Wikipedia test files we got very good results. 

### Author
- Timon Schneider
- Guo Lei