import re
from urllib.parse import urlparse, urldefrag
import lxml
from bs4 import BeautifulSoup
import legal
import textContent
from collections import defaultdict
import json
# also imported urldefrag to "defragment" each URL
# for us to run it in terminal, must pip install
# 1) lxml
# 2) spacetime (look at ed discussion if having difficulty)
# 3) nltk (as of now unless we use a different tokenizer)

IcsUciEduDomains = defaultdict(int)


def scraper(url, resp):
    dictionaryForWebSite = textContent.countTokens(resp) #dictionary with frequency of each word
    if len(dictionaryForWebSite) != 0: #checks if website isnt empty
        writeToFile(dictionaryForWebSite, url) #write to a file to prevent excessive usage of memory
    check_IcsUciEdu(url)
    return extract_next_links(url, resp)

def writeToFile(dictionary, url): #writes the tokens and their frequeny to a file
    with open('URLtokens.txt', 'a') as index_file:
            index_file.write(url)
            index_file.write("\n")
            index_file.write(json.dumps(dictionary))
            index_file.write("\n")

def check_IcsUciEdu(url): #checks if it is a subdomain in the ics.uci.edu domain using a regex pattern(problem 4)
    check_ics_uci_edu_domain = r'^(www\.)?(.*\.)(ics\.uci\.edu)$'
    parsed = urlparse(url)
    global IcsUciEduDomains
    #add it to the dictionary of subdomains if it does containt the correct domain
    #and also prevents the original domain from being added'''
    if re.match(check_ics_uci_edu_domain, parsed.netloc) != None:
        if parsed.netloc != "www.ics.uci.edu" and parsed.netloc != "ics.uci.edu":
            IcsUciEduDomains[parsed.netloc] += 1


def extract_next_links(url, resp):
    ''' Everything in this paragraph is what was given in the template...
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    '''

    # Makes a BeautifulSoup that finds all hyperlinks within that resp.content
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    found_links_content = soup.find_all('a', href=True)
    hyperlinks = set()
    domain = urlparse(url).netloc
    
    # Skipping pages that are just .txt formats of a similar page
    # Skipping pages with query strings
    cannot_contain_keywords = ["format=txt"]

    noFollowLinks = soup.find_all('a', rel="nofollow")
    

    # Goes through the href's found and formats them in full url form to be put
    # in a set(which later is turned into a list)
    # Makes the assumption that implicit href's uses "https://"
    for content in found_links_content:
        href = content['href'] #href is just the entire URL 
        if len(href) != 0 and href[0] != "#" and not any(keyword in href for keyword in cannot_contain_keywords):
            
            #check all links if they are valid before adding it to the set
            if(len(href) > 1 and href[:2] == "//"):
                if is_valid("https:" + href):
                    hyperlinks.add(urldefrag("https:" + href)[0])
            elif(href[0] == '/'):
                if is_valid("https://" + domain + href):
                    hyperlinks.add(urldefrag("https://" + domain + href)[0])
            elif(href != "javascript:void(0)"):
                if is_valid(href):
                    hyperlinks.add(urldefrag(href)[0])

    return list(hyperlinks)



def is_valid(url):
    '''Return bool on whether the url meets
    all conditions.'''
    # Decide whether to crawl this url or not. (before checking robots.txt)
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        # parsed has attributes: scheme, netloc, path, params, query, fragment
        if parsed.scheme not in set(["http", "https"]):
            return False
        check_netloc_pattern = r'^(www\.)?(.*\.)?(ics\.uci\.edu|cs\.uci\.edu|informatics\.uci\.edu|stat\.uci\.edu)$'
        fifth_link_pattern_domain = r'^(www\.)?today.uci.edu$'  # using r strings for pattern recognition when determining if the url is valid or not.
        fifth_link_pattern_path = r'^/department/information_computer_sciences/.*$'
        # doesn't include the fifth domain

        #quick check to make sure doesnt access a file
        try:
            if parsed.path[1] == "~":
                return False
            if parsed.path[1:4] == "files":
                return False
        except:
            pass
    
          
        if re.match(check_netloc_pattern, parsed.netloc) == None:  # first check if no matches with first four websites
            if re.match(fifth_link_pattern_domain, parsed.netloc) != None:
                # then the fifth link matched but we need to check if it has the correct beginning paths
                if re.match(fifth_link_pattern_path, parsed.path) == None:
                    return False
            else:
                return False
        # lines 44 through 50 check if it is a valid domain (and path if it is the fifth link)
        # at this point it should return true and it just has to do the final check on line 54
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        return False    # if type error, we should not add it to frontier
