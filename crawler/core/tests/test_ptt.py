# -*- coding: utf-8 -*-
import pytest
from scrapy.http import HtmlResponse
import urllib
import urllib2
import cookielib
from pprintpp import pprint as pp
import ptt
import datetime
import calendar
from dateutil import parser

class Test_PTT_Board_Scraper(object):

    @pytest.fixture
    def scraper(self):
        scraper = ptt.PTT_Board_Scraper()
        return scraper

    @pytest.fixture
    def response(self):
        url = "https://www.ptt.cc/bbs/Gossiping/index2.html"
        body = urllib2.urlopen(url).read()

        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', 'over18=1'))
        body = opener.open(url).read()
        return HtmlResponse(url=url, body=body)

    def test_get_links(self, scraper, response):
        expected = u'https://www.ptt.cc/bbs/Gossiping/M.1119354366.A.960.html'
        tested = scraper.get_links(response)[0]
        assert expected == tested


    def test_get_timestamps(self, scraper, response):
        year = datetime.datetime.now().year
        hour = datetime.datetime.now().hour
        date = "6/21"

        expected_floor = calendar.timegm(parser.parse("%s/%s %s:0:0" % (year, \
                         date, hour)).timetuple())
        expected_ceil = calendar.timegm(parser.parse("%s/%s %s:59:59" % (year, \
                         date, hour)).timetuple()) + 3600
        # Time zone shifting
        expected_floor -= 28800
        expected_ceil -= 28800
        tested = scraper.get_timestamps(response)[0]
        assert tested >= expected_floor and tested<=expected_ceil

    def test_get_items(self, scraper, response):
        expected = {
            'source': u'Ptt',
            'board_id': 'Gossiping',
            'link': u'https://www.ptt.cc/bbs/Gossiping/M.1119354366.A.960.html',
            'timestamp': 1434897428,
            'previous_page': u'https://www.ptt.cc/bbs/Gossiping/index1.html',
            'enable': 1
        }
        tested = scraper.get_items(response)[0]
        tested.pop('next_update_time', None)
        expected_timestamp = expected.pop('timestamp')
        tested_timestamp = tested.pop('timestamp')
        # assert expected_timestamp <= tested_timestamp
        assert expected == tested
        expected_len = 20
        tested_len = len(scraper.get_items(response))
        assert expected_len == tested_len

    def test_login(self, scraper):
        cj = cookielib.CookieJar()
        login_url = scraper.login_url()
        payload = scraper.login_form()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        login_data = urllib.urlencode(payload)
        opener.open(login_url, login_data)
        resp = opener.open('https://www.ptt.cc/bbs/Gossiping/index2.html')
        body = resp.read()
        response = HtmlResponse(url=login_url, body=body)
        assert scraper.check_login_response(response) == "self.initialized()"


class Test_PTT_Article_Scraper(object):

    @pytest.fixture
    def scraper(self):
        scraper = ptt.PTT_Article_Scraper()
        return scraper

    @pytest.fixture
    def response(self):
        url = "https://www.ptt.cc/bbs/Gossiping/M.1421733623.A.0A1.html"
        """
        ptt.cc, youtube : https://www.ptt.cc/bbs/Gossiping/M.1119222611.A.7A9.html"
        i.imgur.com :"https://www.ptt.cc/bbs/Gossiping/M.1434046480.A.73C.html"
        fb: https://www.ptt.cc/bbs/Gossiping/M.1430487754.A.0B2.html
        imgur.com : "https://www.ptt.cc/bbs/Beauty/M.1423732219.A.614.html"
        """
        body = urllib2.urlopen(url).read()
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', 'over18=1'))
        body = opener.open(url).read()
        return HtmlResponse(url=url, body=body)

    def test_login(self, scraper):
        cj = cookielib.CookieJar()
        login_url = scraper.login_url()
        payload = scraper.login_form()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        login_data = urllib.urlencode(payload)
        opener.open(login_url, login_data)
        resp = opener.open('https://www.ptt.cc/bbs/Gossiping/index2.html')
        body = resp.read()
        response = HtmlResponse(url=login_url, body=body)
        assert scraper.check_login_response(response) == "self.initialized()"

    def test_get_author(self, scraper, response):
        expected = "neepa"
        tested = scraper.get_author(response)
        assert expected == tested

    def test_get_board(self, scraper, response):
        expected = u"Gossiping"
        tested = scraper.get_board(response)
        assert expected == tested

    def test_get_titile(self, scraper, response):
        expected = u"Re: [新聞] 桃園新屋保齡球館大火燒塌 救災六消防隊"
        tested = scraper.get_title(response)
        assert expected == tested

    def test_get_thumbnail(self, scraper, response):
        # someone replied with an image in imgur on 2015/09/22,
        # this article didn't have any image before.
        # The sample has removed all pic therefore set it to ""
        expected = u"http://i.imgur.com/Y2qQqdQ.jpg"
        tested = scraper.get_thumbnail(response)
        assert expected == tested

    def test_get_timestamp(self, scraper, response):
        expected = 1421733620
        tested = scraper.get_timestamp(response)
        assert expected == tested

    def test_get_content(self, scraper, response):
        tested = scraper.get_content(response)
        assert u'作者nee' == tested[0:5]
        assert u'ding2599: 很多警大剛畢業都在指揮 啥都不懂 01/20 14:01' == tested[1100:1150].strip()

    def test_get_comment_list(self, scraper, response):
        tested = scraper._get_comment_list(response)
        expected = [
            u'推 ', u'gallado', u': 1有掛', u' 01/20 14:01\n',
        ]
        assert expected == tested[:4]

    def test_get_socail_stats(self, scraper, response):
        # viewCount does not exist, should be -1
        expected = [0, 0, 12, 0, -1]
        tested = scraper._get_social_stats(response)
        for i, j in zip(expected, tested):
            assert i <= j

    def test_get_rank(self, scraper, response, monkeypatch):
        import sys
        sys.path.append("../crawler")
        import settings
        from rank import Viral_Ranker
        from abstract_db import sqlalchemy_
        def mockinit(self):
            self.get_rank = eval("self." + settings.RANK_METHOD.lower())
            self.db = sqlalchemy_()
        def mockreturn(self, board_id):
            return 1
        def mock_get_fansCount(self, response):
            return 30000
        monkeypatch.setattr(sqlalchemy_, '__init__', lambda self: None)
        monkeypatch.setattr(sqlalchemy_, 'get_board_rank', mockreturn)
        monkeypatch.setattr(Viral_Ranker, '__init__', mockinit)
        monkeypatch.setattr(ptt.PTT_Article_Scraper, '_get_fansCount', mock_get_fansCount)
        expected = 0.295644
        tested = scraper.get_rank(response)
        assert expected == tested
