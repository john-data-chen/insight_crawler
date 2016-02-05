# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from core.scraper import *
from scrapy.spiders.init import InitSpider
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.http import Request
from scrapy.http import FormRequest
from pprintpp import pprint as pp
from core.initSpider import initDefault
from core.error_handler import Scraper_Error_Handler
from crawler import settings
from pprintpp import pprint as pp


class CrawlerSpider(InitSpider):
    name = "crawler"
    handle_httpstatus_list = [404]
    rules = (
        Rule(LinkExtractor(allow=r''),
             callback='parse', follow=True),
    )

    def __init__(self, scraper='', CRAWLER_COUNT='', CRAWLER_ID='', start_urls=''):
        source = scraper.split("_")[0].lower()
        crawling_type = scraper.split("_")[1].lower()
        # Run-time decide loading ptt, youtube, facebook, ...
        exec("from core." + source + " import " + scraper + " as Scraper")
        # for pipeline
        self.crawling_type = crawling_type

        scraper = Scraper()
        self.scraper = scraper
        self.init_dafault = initDefault()

        if CRAWLER_COUNT == CRAWLER_ID == '':
            CRAWLER_ID = settings.CRAWLER_ID
            CRAWLER_COUNT = settings.CRAWLER_COUNT
        CRAWLER_ID = int(CRAWLER_ID)
        CRAWLER_COUNT = int(CRAWLER_COUNT)
        source = source.title()
        crawling_type = crawling_type.title()

        if start_urls !='' :
            self.start_urls = start_urls.split(',')
        else:
            self.start_urls = scraper.start_urls(source, crawling_type,
                                             CRAWLER_ID, CRAWLER_COUNT)

        if len(self.start_urls) == 0:
            from scrapy.exceptions import CloseSpider
            raise CloseSpider('no more stuff to crawl')

        if "allowed_domains" in dir(scraper):
            self.allowed_domains = scraper.allowed_domains()

        if "login_url" in dir(scraper):
            self.login_url = scraper.login_url()
        else:
            self.login_url = self.start_urls[0]

        self.check_login_response = self._check_login_response
        self.login = self._login

    def init_request(self):
        return Request(url=self.login_url, callback=self.login)

    def _login(self, response):
        if "login" in dir(self.scraper):
            return eval(self.scraper.login(response))
        else:
            return eval(self.init_dafault.login(response))

    def _check_login_response(self, response):
        if "check_login_response" in dir(self.scraper):
            return eval(self.scraper.check_login_response(response))
        else:
            return eval(self.init_dafault.check_login_response(response))

    def parse(self, response):
        # http://stackoverflow.com/questions/18691333/returning-generators-in-python
        # http://milinda.pathirage.org.s3-website-us-east-1.amazonaws.com/python/scrapy/2012/03/13/recursively_scraping_blog_with_scrapy.html
        if response.status == 404:
            scraper_error_handler = Scraper_Error_Handler()
            scraper_error_handler.process_item_error(response)
            #raise CloseSpider('404 found at %s' % response.url)

        if "Board_Scraper" in self.scraper.__class__.__name__:
            items = self.scraper.get_items(response)
            if "get_previous_page" in dir(self.scraper) and response.meta["depth"]<5 and len(items) > 0 and 'previous_page' in items[0]:
                import logging
                logging.error("Recursively Scraping: " + str(response.meta["depth"]))
                yield Request(items[0]['previous_page'], callback = self.parse)
            # let's return item
            if items == None:
                print "no items", response.url
            else:
                for item in items:
                    item.pop('previous_page', None)
                    yield item
        else:
            item = self.scraper.get_item(response)
            yield item
            """
            item = self.scraper.get_item(response)
            # let's return item
            return item
            """

