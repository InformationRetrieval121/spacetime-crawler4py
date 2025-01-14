# textContent.py
import lxml
from bs4 import BeautifulSoup
from collections import defaultdict
import math
import nltk
import re
nltk.download("punkt")
# pip install nltk

mostWordsCount = 0
mostWordsURL = ""

#sorted list of words (allows us to use binary search) that we want to skip, irrelevant words 
stopWords = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
biggestIndexForStopWords = len(stopWords) - 1
ultimateDictionary = defaultdict(int)   # this dictionary will be used to add all found words
                                        # across all found web sites


def findTop50(): #returns a list containing the top 50 words that appeared across all sites
    global ultimateDictionary #global because we use it across all websites 
    mostCommon = []
    i = 0
    #sort dictioanry by the value(number of times the word appears) in ascending order
    for k,v in sorted(ultimateDictionary.items(), key=(lambda t : -t[1])):
        if i >= 50:
            break
        else:
            mostCommon.append(k)
        i += 1
    return mostCommon

def countTokens(resp):
    ''' Take in a response object and tokenize important
    words from the web site. Returns a dictionary of
    words found with frequency.'''

    wordFreq = defaultdict(int)     # current dictionary of words for this web site
    count = 0   # local total number of words found in this web site
    
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser', from_encoding="utf-8")
    entireBodyTag = soup.body
    
    alphaNumericPattern = r'^[a-zA-Z0-9]$'

    global biggestIndexForStopWords
    global ultimateDictionary
    
    if entireBodyTag is not None:
        for s in entireBodyTag.strings:     # gets every "sentence" in the web site (headers/body/etc)
            tokenizedList = nltk.tokenize.word_tokenize(s.strip())  # gets rid of surrounding whitespace/newlines and tokenizes sentence into a list
            for element in tokenizedList:   # looping through each actual token
                try:
                    element = element.lower()   # normalize the word to all lower case
                except:
                    pass
                
                if len(element) == 1 and re.match(alphaNumericPattern, element) != None:
                    # means that it is an actual single letter "word" and not a special symbol
                    count += 1
                    if not (binarySearch(element, 0, biggestIndexForStopWords)):
                    # enters if it is a single alphanumeric character (not special symbols) that is not a stop word
                        wordFreq[element] += 1  # keep even one letter "words" in indexing dictionary though
                        # ultimateDictionary[element] += 1  # don't add to dictionary of top 50 since only doing non stop words and len must be >= 3
                elif len(element) > 1:
                    count += 1
                    if not (binarySearch(element, 0, biggestIndexForStopWords)):
                    # enters if it is a word that is bigger than just one character and also not a stop word
                        wordFreq[element] += 1
                        if len(element) >= 3:   # only adding len >= 3 words that aren't stopwords
                            try:
                                throwawayNumber = float(element)    # if element is a number, don't add it to dictionary
                            except ValueError:                      # ValueError only is thrown if it is not a number since calling float("word") isn't possible
                                ultimateDictionary[element] += 1
                  

    global mostWordsCount
    global mostWordsURL
            
    if len(wordFreq) < 30 or len(wordFreq) > 10000: # getting rid of low value page with under 30 different words in the entire web siteand large files in terms of "keys"
        return {}                                   # getting rid of files which may contain so much information to the point that the information is not reliable (more than 10,000 different words)
    
    if count > mostWordsCount: # keeps track of the biggest URL, updating the old "biggest one" when we find one even bigger 
        mostWordsCount = count
        mostWordsURL = resp.url

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
