# worker.py

from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import legal
import textContent
from collections import defaultdict
from urllib.parse import urlparse

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.allVisited = defaultdict(int)  # dictionary containing all visited URLs without query and fragment 
        self.bannedURLS = []    # the bannedURLs that were traps 
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                allUniques = 0
                for value in self.allVisited.values():
                    allUniques += value
                # these loggers used to output the information needed for problems1-4
                self.logger.info(f"(1) Unique Pages found: {allUniques}")
                self.logger.info(f"(2) Longest page in terms of # of words: {textContent.mostWordsURL} with {textContent.mostWordsCount} words.")
                FiftyMostCommon = textContent.findTop50()
                self.logger.info(f"(3) 50 most common words: {FiftyMostCommon}")
                self.logger.info("(4) List of subdomains alphabetically and number of unique pages...")
                for k,v in sorted(scraper.IcsUciEduDomains.items(), key=(lambda t : t[0])): #sorts them in alphabetical order
                    self.logger.info(f"{k}, {v}")
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            parsed = urlparse(tbd_url)

            # removes the query, fragment, and trailing "/" of path from URL
            # does this ^ to get the URL that could lead to query traps and repeating path traps
            checkConditionURL = tbd_url.replace("?" + parsed.query, "")
            checkConditionURL = checkConditionURL.replace("#" + parsed.fragment, "")
            if checkConditionURL[-1] == "/":
                checkConditionURL = checkConditionURL[:len(checkConditionURL)-1]

            # checks if the URL is already banned or not
            BannedFlag = False
            for bannedLink in self.bannedURLS:
                if checkConditionURL[:len(bannedLink)] == bannedLink:
                    BannedFlag = True
                    
            # increments amount of times that URL has been visited (checking for traps) and also bans the trap URLs
            # preventing the download of trap URLs as this check is done before actually downloading the URLs
            if (not BannedFlag) and (checkConditionURL not in self.allVisited or self.allVisited[checkConditionURL] < 25):  # 25 is the threshold for the amount of different queries a certain url can have before we block it
                self.allVisited[checkConditionURL] += 1
                if self.allVisited[checkConditionURL] == 1:  # if == 1, may be a "unique path" for traps that generate dates by changing end of path i.e. /1-2022/ or /2-2022/ and so on
                    if parsed.path != "":                            
                        mostOfURL = checkConditionURL.rfind("/") # index for last slash in a URL 
                        mainpartOfURL = checkConditionURL[:mostOfURL] # https://www.brian.com/events/2000-11-22 ----> https://www.brian.com/events
                        repeats_num = 0
                        for key in self.allVisited.keys():
                            if key[:mostOfURL].count("/") > 2 and key[:mostOfURL] == mainpartOfURL: # possibly ban a url IF it is not a domain (hence the most have 3 or more slashes in the url (shouldn't ban https://ics.uci.edu)
                                repeats_num += 1
                                if repeats_num > 145: # The amount 145 is our threshold to decide we are in a trap relating to changing end of path names (calendar traps being an example)
                                    self.bannedURLS.append(mainpartOfURL)
                                    break # important because it saves us time from always iterating through all of the keys 

                if legal.checkLegality(tbd_url, self.config):	        # if legal...
                    resp = download(tbd_url, self.config, self.logger)  # then download the web site
                    self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                    if resp.status == 200:  # if not status 200, we can't access any reasonable information for the web site
                        scraped_urls = scraper.scraper(tbd_url, resp)
                        for scraped_url in scraped_urls:
                            self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
