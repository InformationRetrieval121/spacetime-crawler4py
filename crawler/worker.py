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
        self.allVisited = defaultdict(int)
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
                self.logger.info(f"(1) Unique Pages found: {allUniques}")
                self.logger.info(f"(2) Longest page in terms of # of words: {textContent.mostWordsURL}")    # this should work
                FiftyMostCommon = textContent.findTop50()
                self.logger.info(f"(3) 50 most common words: {FiftyMostCommon}")
                self.logger.info("(4) List of subdomains alphabetically and number of unique pages...")
                for k,v in sorted(scraper.IcsUciEduDomains.items(), key=(lambda t : t[0])):
                    self.logger.info(f"{k}, {v}")
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            parsed = urlparse(tbd_url)
            checkConditionURL = tbd_url.replace(parsed.query, "")
            checkConditionURL = tbd_url.replace(parsed.fragment, "")

            if checkConditionURL not in self.allVisited or self.allVisited[checkConditionURL] < 20:
                self.allVisited[tbd_url] += 1
                if legal.checkLegality(tbd_url, self.config):	# if not visited before and legal...
                    resp = download(tbd_url, self.config, self.logger)  # then download the web site
                    self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                    if resp.status == 200:  # if not status 200, we can't access any reasonable information for the web site
                        scraped_urls = scraper.scraper(tbd_url, resp)
                        for scraped_url in scraped_urls:
                            self.frontier.add_url(scraped_url)
            else:
                print(checkConditionURL, "executed too many times:", self.allVisited[checkConditionURL])

            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
