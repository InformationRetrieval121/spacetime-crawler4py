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

mostWordsCount = 0
mostWordsURL = ""

# sorted already so we can use binary search
stopWords = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
biggestIndexForStopWords = len(stopWords) - 1
ultimateDictionary = defaultdict(int)   # this dictionary will be used to add all found words
                                        # across all found web sites
def findTop50():
    global ultimateDictionary
    mostCommon = []
    i = 0
    for k,v in sorted(ultimateDictionary.items(), key=(lambda t : t[1])):
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
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser', from_encoding="utf-8")
    entireBodyTag = soup.body
    count = 0   # local total number of words found in this web site

    global biggestIndexForStopWords
    global ultimateDictionary
    
    if entireBodyTag is not None:
        for s in entireBodyTag.strings:     # gets every "sentence" in the web site (headers/body/etc)
            tokenizedList = nltk.tokenize.word_tokenize(s.strip())  # tokenizes each sentence and gets rid of surrounding whitespace/newlines
            for element in tokenizedList:   # looping through each actual token/word
                count += 1
                if not (binarySearch(element, 0, biggestIndexForStopWords)):
                    wordFreq[element] += 1
                    ultimateDictionary[element] += 1

    global mostWordsCount
    global mostWordsURL
                
    if count > mostWordsCount:
        mostWordsCount = count
        mostWordsURL = resp.url
        # print("mostWordsURL: " + str(mostWordsURL) + "     mostWordsCount: " + str(mostWordsCount))
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

"""
#attempting to implement approach described in page# 61 of our textbook (lecture 11 slides)
#to eliminate near duplicates

#zip(src_words,src_words[1:],src_words[2:]) #optimally extract different N ngrams simultaneously, when N=3 
#so this? -> zip(tokenizedList,tokenizedList[1:],tokenizedList[2:]) 
def fingerprint(hyperlinks)
    urlTriGrams = defaultdict(list) #consisting of {hyperlink, 3-gram of tokenized values of hyperlinks' content}
    for hyperlink in hyperlinks:
        urlTriGrams[hyperlink] = generate_n_grams(tokenizedList, 3) #storing 3-gram for each hyperlink
        for element in urlTriGrams[hyperlink]:
            element = hashlib.sha1(element) #make each element a hash value (hash with checksum instead)

"""

