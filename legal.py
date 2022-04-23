# legal.py

# parsed has attributes: scheme, netloc, path, params, query, fragment
# used to break up url's by parts
from urllib.parse import urlparse

#used to download robots.txt file of the web sites
from utils.download import download

    
def checkLegality(given_url, given_config):
    '''Takes a url, downloads the domain's robots.txt file,
    checks if allowed to crawl or not. Returns bool.'''
    if len(given_url) > 200:    # don't visit any url's with length greater than 200 since some 
        return False            # traps repetitively append a  path to the url

    parsedResult = urlparse(given_url)  # split up the url into its parts
    
    urlCheckingFor = given_url
    # assures 1) query is empty, 2) fragment is empty, 3) path is not empty, 4) last character is not a slash
    if parsedResult.query == "" and parsedResult.fragment == "" and parsedResult.path != "" and parsedResult.path[-1] != "/":
        urlCheckingFor += "/"    # add a slash to the end of the url if it is not there
        
    urlWithRobot = parsedResult.scheme + "://" + parsedResult.netloc + "/robots.txt"    # url of robots.txt
    try:
        resp = download(urlWithRobot, given_config) # download the robots.txt file from cache
        if resp.status == 200:      # only continue if we were able to download the robots.txt file correctly
            allLines = resp.raw_response.content.decode("utf-8").split('\n')    # all lines of robots.txt stored into a list
            appliesToOurBot = False # an indicator of whether the "laws" apply to our bot (User agent must be *)
            disallowedPaths = []    # stores paths disallowed applicable to our bot
            allowedPaths = []       # stores paths allowed (after being disallowed) applicable to our bot
            for lineToRead in allLines: # reads the all lines of robots.txt
                if len(lineToRead) != 0:    # skip over a line if it has no characters
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

            lenOfLongestDP = 0 # length of biggest disallowed url that applies to the "urlCheckingFor" (see bottom of file to see example of why we must find biggest disallowed)
            for disallowedPath in disallowedPaths:
                lenOfCurrentDP = len(disallowedPath)
                if (disallowedPath == urlCheckingFor[:lenOfCurrentDP]) and lenOfCurrentDP > lenOfLongestDP: # only disallow if it matches and bigger than previous biggest disalllowed url
                    lenOfLongestDP = lenOfCurrentDP
                    isLegal = False     # as of right now, our url is disallowed                                

            if isLegal:     # if no disallowed paths matched ours, immediately... 
                return True 

            for allowedPath in allowedPaths:
                if allowedPath == urlCheckingFor[:len(allowedPath)] and len(allowedPath) > lenOfLongestDP:  # make sure it is BIGGER than the biggest disallowed path found
                    return True
            return False  # means no "allow" statements overrided the disallowed path
        else:
            return False # this executes when access robots.txt file (not status 200) for traps
            
    except:
        return False     # this executes if download went wrong and something failed (for intentional traps) that perhaps don't provide a robots.txt file

'''
User-agent: *
Disallow: /something/
Disallow: /something/important/topsecret/
Allow: /something/important/
'''
