import re
from urllib.parse import urlparse, urldefrag
# also imported urldefrag to "defragment" each URL

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [urldefrag(link)[0] for link in links if is_valid(link)]

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
    if resp.status != 200:
        # error so don't do anything
        return list()
    else:
        print(resp.raw_response.url)
        pritn(resp.raw_response.content)
        return list()
    

def is_valid(url):
    '''Return bool on whether the url meets
    all conditions.'''
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        # parsed has attributes: scheme, netloc, path, params, query, fragment
        # parsed_defrag = urlparse(urldefrag(url)[0]) # gets rid of frag but may be unecessary
        if parsed.scheme not in set(["http", "https"]):
            return False
        check_netloc_pattern = r'^(www\.)?(.*\.)?(ics\.uci\.edu|cs\.uci\.edu|informatics\.uci\.edu|stat\.uci\.edu)$'
        fifth_link_pattern_domain = r'^(www\.)?today.uci.edu$'
        fifth_link_pattern_path = r'^/department/information_computer_sciences/.*$'
        # doesn't include the fifth domain
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
        print ("TypeError for ", parsed)
        raise

