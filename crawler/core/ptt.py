# -*- coding: utf-8 -*-
from dateutil import parser
import calendar
from scrapy.item import Item, Field
# from scrapy import FormRequest
from scrapy import Request
import re
from scraper import Scraper_Base
# from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
import time
import urllib2, json
from core.abstract_db import *
import datetime
from rank import Viral_Ranker
from abstract_sample import Sample_data


class PTT_Article_Scraper(Scraper_Base):

    def __init__(self):
        self.stats = None
        self.url = None
        Scraper_Base.__init__(self)

    def login_form(self):
        return {'yes': 'yes'}

    def login_url(self):
        return ("https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html")

    def login(self, response):
        return "FormRequest.from_response(response, formdata=%s,\
                callback=self.check_login_response) " % str(self.login_form())

    def check_login_response(self, response):
        if "bbs-screen bbs-footer-message" in response.body:
            return "self.initialized()"
        else:
            return ""

    def get_source(self, response):
        return u"Ptt"

    def get_author(self, response):
        xpath = "//span[@class='article-meta-value']/text()"
        author_with_nickname = response.xpath(xpath).extract()[0]
        index_nick = author_with_nickname.index(u"(")
        return author_with_nickname[:index_nick-1]

    def get_board_id(self, response):
        return self.get_board(response)

    def get_board(self, response):
        xpath = "//a[@class='board']/text()"
        return response.xpath(xpath).extract()[0]

    def get_title(self, response):
        xpath = "//span[@class='article-meta-value']/text()"
        return response.xpath(xpath).extract()[2]

    def get_link(self, response):
        if 'redirect_urls' in response.request.meta:
            return response.request.meta['redirect_urls']
        else:
            return response.url

    def get_description(self, response):
        return u""

    def get_thumbnail(self, response):
        result = []
        links = response.xpath("//a[@href]//text()").extract()
        for link in links:
            parsed_link = re.findall(r'(http://.*\.jpg)', link)
            result.extend(parsed_link)
            parsed_link = re.findall(r'(http://.*\.gif)', link)
            result.extend(parsed_link)
            parsed_link = re.findall(r'(http://.*\.jpeg)', link)
            result.extend(parsed_link)
            """
            parsed_link = re.findall(r'(http://i.imgur.com/.*\.jpg)', link)
            result.extend(parsed_link)

            parsed_link = re.findall(r'(http://imgur.com/.*)', link)
            # http://imgur.com/6Y6Yv4C => http://i.imgur.com/6Y6Yv4C.png?1"
            if len(parsed_link) != 0:
                for _link in parsed_link:
                    _link = _link.replace("imgur/", "i.imgur")
                    result.extend(_link)
            """
            """
            parsed_link = re.findall(r'(http://www.youtube.com/watch\?.*)', link)
            result.extend(parsed_link)
            parsed_link = re.findall(r'(http://youtu.be/.*)', link)
            result.extend(parsed_link)
            parsed_link = re.findall(r'(http://ppt.cc/.*)', link)
            result.extend(parsed_link)
            parsed_link = re.findall(r'(http://www.facebook.com/.*)', link)
            result.extend(parsed_link)
            """

        if len(result) != 0:
            return result[0]
        return u""

    def get_content(self, response):
        xpath = "//div[@id='main-content']//text()"
        return u"".join(response.xpath(xpath).extract())

    def get_timestamp(self, response):
        xpath = "//span[@class='article-meta-value']/text()"
        datetime = response.xpath(xpath).extract()[3].encode('utf-8')
        return calendar.timegm(parser.parse(datetime).timetuple()) - 28800

    def get_likeCount(self, response):
        return self._get_social_stats(response)[0]

    def get_shareCount(self, response):
        end_point = "http://api.facebook.com/restserver.php?method=links.getStats&format=json&urls="
        query_url = response.url
        api_link = end_point + query_url
        result = urllib2.urlopen(api_link)
        stats = json.load(result)
        return stats[0]['share_count']

    def get_dislikeCount(self, response):
        return self._get_social_stats(response)[2]

    def get_commentCount(self, response):
        return self._get_social_stats(response)[3]

    def get_viewCount(self, response):
	    # not exists = -1
        return self._get_social_stats(response)[4]

    def get_fansCount(self, response):
        return self._get_social_stats(response)[5]

    def _get_fansCount(self, response):
        board_id = self.get_board_id(response)
        sample = Sample_data()
        fansCount = 0
        ptt_boards = sample.get_ptt_board_sample()
        for board in ptt_boards:
            if board['board_id'].lower() == board_id.lower():
                fansCount = board['fansCount']
        if fansCount == 0:
            return 1
        else:
            return fansCount

    def get_rank(self, response):
        stats = {}
        stats['board_id'] = self.get_board_id(response)
        stats['likeCount'] = self.get_likeCount(response)
        stats['dislikeCount'] = self.get_dislikeCount(response)
        stats['viewCount'] = self.get_viewCount(response)
        stats['shareCount'] = self.get_shareCount(response)
        stats['commentCount'] = self.get_commentCount(response)
        stats['fansCount'] = self.get_fansCount(response)
        viral_ranker = Viral_Ranker()
        return viral_ranker.get_rank(stats)

    def get_location(self, response):
        return u""

    def get_post_type(self, response):
        return u"post"

    def _get_ip(self, response):
        xpath = "//span[@class='f2']/text()"
        _ip_line = response.xpath(xpath).extract()[0].encode('utf-8')
        return re.findall(r'[0-9]+(?:\.[0-9]+){3}', _ip_line)

    def _get_comment_list(self, response):
        # this is a list
        xpath = "//div[@class='push']//text()"
        comments = response.xpath(xpath).extract()
        return comments

    def _get_social_stats(self, response):
        if self.url == response.url:
            return self.stats
        # index
        i = 0
        # tag counts
        likeCount, shareCount, commentCount, dislikeCount, fansCount = 0, 0, 0, 0, 0
        # not exists = -1
        viewCount = -1
        comments = self._get_comment_list(response)
        # create a while loop to count push / dislike / -> tags
        while True:
            try:
                # there are 4 elements in one set of comments
                # the 1st element is the target
                # this is push tag counter
                if comments[i][0] == u'\u63a8':
                    likeCount += 1
                # this is dislike tag counter
                if comments[i][0] == u'\u5653':
                    dislikeCount += 1
                # this is -> tag counter
                if comments[i][0] == u'\u2192':
                    commentCount += 1
                # there are 4 elements in one set of comments
                # +4 to the next comment
                i += 4
            # when no element can be counted, exit while loop
            except IndexError:
                break

        fansCount = self._get_fansCount(response)
        commentCount = (commentCount + likeCount + dislikeCount)
        self.stats = [likeCount, shareCount, dislikeCount, commentCount, viewCount, fansCount]
        self.url = response.url
        return self.stats


class PTT_Board_Scraper(Scraper_Base):

    def __init__(self):
        Scraper_Base.__init__(self)

    def login_form(self):
        return {'yes': 'yes'}

    def login_url(self):
        return ("https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html")

    def get_source(self, response):
        return u"Ptt"

    def login(self, response):
        return "FormRequest.from_response(response, formdata=%s,\
                callback=self.check_login_response) " % str(self.login_form())

    def check_login_response(self, response):
        if "bbs-screen bbs-footer-message" in response.body:
            return "self.initialized()"
        else:
            return ""

    def get_board_id(self, response):
        """
        https://www.ptt.cc/bbs/Gossiping/index10342.html
        """
        return response.url.split("/")[-2]

    def get_next_update_time(self, response):
        return int(time.time())

    def get_links(self, response):
        xpath = 'div[class=title] a::attr(href)'
        prefix = "https://www.ptt.cc"
        return [prefix + link for link in response.css(xpath).extract()]

    def get_previous_page(self, response):
        xpath = "//div[@class='btn-group pull-right']/a/@href"
        prefix = "https://www.ptt.cc"
        return prefix + response.xpath(xpath).extract()[1]

    def _scrape_next_page(self, response):
        return Request(self._get_previous_page(response), callback=self.parse)

    def get_timestamps(self, response):
        year = datetime.datetime.now().year
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        second = datetime.datetime.now().second
        dates = response.xpath("//div[@class='date']//text()").extract()
        return [calendar.timegm(parser.parse("%s/%s %s:%s:%s" % (year, date, \
                hour, minute, second)).timetuple()) - 28800 for date in dates]

    def get_enables(self, response):
        return True

class PTT_Article_Scraper_Item(Item):
    class_name = "PTT_Article_Scraper"
    scraper_item = Scraper_Base()
    exec(scraper_item._get_item_definition(class_name))


class PTT_Board_Scraper_Item(Item):
    class_name = "PTT_Board_Scraper"
    scraper_item = Scraper_Base()
    exec(scraper_item._get_item_definition(class_name))
