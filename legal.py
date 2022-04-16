# legal.py

from urllib.parse import urlparse
import urllib.request

# THIS ALL NEEDS TO BE PUT INSIDE OF A FUNCTION (NOT DONE)
# NEEDS TO ALSO HANDLE "*" WHEN USED IN THE CONTEXT OF Disallow

# writing the code so it works for every robots.txt file though

# parsed has attributes: scheme, netloc, path, params, query, fragment
# parsed_defrag = urlparse(urldefrag(url)[0]) # gets rid of frag but may be unecessary
def checkLegality(given_url):
    print("IN CHECK LEGALITY:", given_url)
    # need to make sure to add "/" to the end of the url if
    # it doesn't have it (but also has to make sure that
    # it is not a url that ends in something like .pdf because
    # then we would be messing the url up)
    parsedResult = urlparse(given_url)
    urlWithRobot = parsedResult.scheme + "://" + parsedResult.netloc + "/robots.txt"
    try:
        response = urllib.request.urlopen(urlWithRobot) # get Response Object
        lineToRead = response.readline().decode('UTF-8')    # get first line of robots.txt file
        appliesToOurBot = False # an indicator of whether we the "laws" apply to our bot
        
        disallowedPaths = []
        allowedPaths = []
        while lineToRead != "": # reads the robots.txt until there is no more content
            splitLine = lineToRead.split()
            if splitLine[0] == 'User-agent:':
                if splitLine[1] == '*':
                    appliesToOurBot = True
                else:
                    appliesToOurBot = False
            elif appliesToOurBot:
                if splitLine[0] == 'Disallow:':
                    if splitLine[1] == "/":
                        return False # return False
                    else:
                        disallowedPaths.append(parsedResult.scheme + "://" + parsedResult.netloc + splitLine[1])
                if splitLine[0] == 'Allow:':
                    allowedPaths.append(parsedResult.scheme + "://" + parsedResult.netloc + splitLine[1])    
            lineToRead = response.readline().decode('UTF-8')

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
        return True # replace with "return True"

if __name__ == "__main__":
    test_url = "https://www.informatics.uci.edu/research" # FIXED BUG
    print(checkLegality(test_url))

# "https://www.informatics.uci.edu/robots.txt
# looks like
'''
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Allow: /research/labs-centers/
Allow: /research/areas-of-expertise/
Allow: /research/example-research-projects/
Allow: /research/phd-research/
Allow: /research/past-dissertations/
Allow: /research/masters-research/
Allow: /research/undergraduate-research/
Allow: /research/gifts-grants/
Disallow: /research/
'''

''' Can this exist?       code works for this situation now
Disallow: /research/
Allow: /research/gifts-grants/
Disallow: /research/gifts-grants/particular/
'''
