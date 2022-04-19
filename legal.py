# legal.py
from urllib.parse import urlparse
from utils.download import download

# parsed has attributes: scheme, netloc, path, params, query, fragment
    
def checkLegality(given_url, given_config):
    '''Takes a url, downloads the domain's robots.txt file,
    checks if allowed to crawl or not. Returns bool.'''
    parsedResult = urlparse(given_url)  # split up the url into its parts
    
    urlCheckingFor = given_url
    if parsedResult.query == "" and parsedResult.fragment == "" and parsedResult.path != "":    # these three lines of code "fixes" any url's
        urlCheckingFor += "/"                                                                   # with paths that don't have a "/" at the end
        
    urlWithRobot = parsedResult.scheme + "://" + parsedResult.netloc + "/robots.txt"    # url of robots.txt
    try:
        resp = download(urlWithRobot, given_config) # download the robots.txt file from cache
        if resp.status == 200:      # only continue if we were able to download the robots.txt file correctly
            allLines = resp.raw_response.content.decode("utf-8").split('\n')    # all lines of robots.txt stored into a list
            appliesToOurBot = False # an indicator of whether we the "laws" apply to our bot
            disallowedPaths = []    # stores paths disallowed applicable to our bot
            allowedPaths = []       # stores paths allowed (after being disallowed) applicable to our bot
            for lineToRead in allLines: # reads the all lines of robots.txt
                if len(lineToRead) != 0:
                    splitLine = lineToRead.split()
                    if splitLine[0] == 'User-agent:' and len(splitLine) > 1:    # check if list has 2 or more elements so splitLine[1] doesn't raise an error
                        if splitLine[1] == '*':
                            appliesToOurBot = True
                        else:
                            appliesToOurBot = False
                    elif appliesToOurBot:
                        if splitLine[0] == 'Disallow:':
                            if splitLine[1] == "/":
                                return False    # this means our bot isn't allowed to crawl anything so return false
                            else:
                                disallowedPaths.append(parsedResult.scheme + "://" + parsedResult.netloc + splitLine[1])    # adding absolute disallowed url (NOT just the relative path)
                        if splitLine[0] == 'Allow:':
                            allowedPaths.append(parsedResult.scheme + "://" + parsedResult.netloc + splitLine[1])    

            isLegal = True  # an indicator to see if we have to check the "allowed" list

            lenOfLongestDP = 0      # look at comment below for why we need to find the "biggest" disallowed path
            for disallowedPath in disallowedPaths:
                lenOfCurrentDP = len(disallowedPath)
                if (disallowedPath == urlCheckingFor[:lenOfCurrentDP]) and lenOfCurrentDP > lenOfLongestDP:   # look at "Can this exist?" comment
                    lenOfLongestDP = lenOfCurrentDP
                    isLegal = False     # as of right now, our url is disallowed                                
            if isLegal:     # if no disallowed paths matched ours, immediately... 
                return True 
            for allowedPath in allowedPaths:
                if allowedPath == urlCheckingFor[:len(allowedPath)] and len(allowedPath) > lenOfLongestDP:# make sure it is BIGGER than the biggest disallowed path found
                    return True # will return True since it found it was allowed
            return False  # means no exceptions were made in the disallowed path
        else:
            return True # assume we can crawl if we can't access robots.txt file (not status 200)
            
    except:
        return True     # assume we can crawl if download went wrong and something failed

'''
User-agent: *
Disallow: /something/
Disallow: /something/important/topsecret/
Allow: /something/important/
'''
