# textContent.py
import lxml
from bs4 import BeautifulSoup
from collections import defaultdict
import math
import nltk
nltk.download("punkt")
# pip install nltk
# also need to credit the authors
# we can either keep this tokenizer or make our own
# this one doesn't split contraction or hyphenated words

stopWords = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
biggestIndexForStopWords = len(stopWords) - 1

def binary_search(stops, word):
	first = 0
	last = len(stops) - 1

	while(first <= last):
		mid = (first + last) // 2
		if stop[mid] == word:
			return True
		elif word < stop[mid]:
			last = mid - 1
		else:
			first = mid + 1	
	return False

def countTokens(resp):
    ''' Take in a response object and tokenize important
    words from the web site. Returns a dictionary of
    words found with frequency.'''

    wordFreq = defaultdict(int)
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser', from_encoding="utf-8")
    entireBodyTag = soup.body
    
    for s in entireBodyTag.strings:
        tokenizedList = nltk.tokenize.word_tokenize(s.strip())
        for element in tokenizedList:
            if not (binarySearch(element, 0, biggestIndexForStopWords)):
                wordFreq[element] += 1

    return wordFreq

def binarySearch(word, small_index, big_index):
    '''Binary Search using the global stop words list to see
    if the word given is a stop word or not. If it is a stop word, return
    True (so don't put in dictionary). If false, put word in dictionary.'''
    if small_index > big_index:
        return False
    else:
        mid_index = math.floor((big_index+small_index)/2)
        if word == stopWords[mid_index]:
            return True
        elif word < stopWords[mid_index]:
            return binarySearch(word, small_index, mid_index-1)
        else:
            return binarySearch(word, mid_index+1, big_index)

