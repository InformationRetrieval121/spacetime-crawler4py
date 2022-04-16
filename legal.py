# legal.py
from urllib.parse import urlparse
from utils.download import download

# parsed has attributes: scheme, netloc, path, params, query, fragment
# parsed_defrag = urlparse(urldefrag(url)[0]) # gets rid of frag but may be unecessary

def checkLegality(given_url, given_config):
    # need to make sure to add "/" to the end of the url if
    # it doesn't have it (but also has to make sure that
    # it is not a url that ends in something like .pdf because
    # then we would be messing the url up)
    parsedResult = urlparse(given_url)
    urlWithRobot = parsedResult.scheme + "://" + parsedResult.netloc + "/robots.txt"
    try:
        resp = download(urlWithRobot, given_config) # download the robots.txt file from cache
        allLines = resp.raw_response.content.decode("utf-8").split('\n')
        appliesToOurBot = False # an indicator of whether we the "laws" apply to our bot
        disallowedPaths = []
        allowedPaths = []
        for lineToRead in allLines: # reads the all lines of robots.txt
            if len(lineToRead) != 0:
                splitLine = lineToRead.split()
                if splitLine[0] == 'User-agent:':
                    if splitLine[1] == '*':
                        appliesToOurBot = True
                    else:
                        appliesToOurBot = False
                elif appliesToOurBot:
                    if splitLine[0] == 'Disallow:':
                        if splitLine[1] == "/":
                            return False
                        else:
                            disallowedPaths.append(parsedResult.scheme + "://" + parsedResult.netloc + splitLine[1])
                    if splitLine[0] == 'Allow:':
                        allowedPaths.append(parsedResult.scheme + "://" + parsedResult.netloc + splitLine[1])    

        # After while loop, do work to check if allowed or disallowed
        isLegal = True  # an indicator to see if we have to check the "allowed" list

        lenOfLongestDP = 0
        for disallowedPath in disallowedPaths:
            lenOfCurrentDP = len(disallowedPath)
            if (disallowedPath == given_url[:lenOfCurrentDP]) and lenOfCurrentDP > lenOfLongestDP:   # look at "Can this exist?" comment
                lenOfLongestDP = lenOfCurrentDP
                isLegal = False                                     # if it can, we need to find the "biggest" disallowed Path
                                               # to make sure we don't prematurely allow it even though it was supposed to be disallowed
        if isLegal:     # was not found to be disallowed so return true here, if not, continue the code
            return True
        for allowedPath in allowedPaths:
            if allowedPath == given_url[:len(allowedPath)] and len(allowedPath) > len(longest_disallowedPath_found):     # make sure it is BIGGER than the biggest disallowed path found
                return True # will return True since it found it was allowed
        return False  # will only execute if wasn't found in allowed (will be False)
            
    except:
        return True
