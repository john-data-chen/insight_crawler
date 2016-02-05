# -*- coding: utf-8 -*-
import pytest
from scrapy.http import HtmlResponse
import urllib2
from pprintpp import pprint as pp
import youtube


class Test_Youtube_Article_Scraper(object):

    @pytest.fixture
    def scraper(self):
        scraper = youtube.Youtube_Article_Scraper()
        return scraper

    @pytest.fixture
    def response(self):
        url = "https://www.youtube.com/watch?v=rXtLH4MJ8u8"
        body = urllib2.urlopen(url).read()
        return HtmlResponse(url=url, body=body)

    def test_get_title(self, scraper, response):
        expected = u"dudu test"
        tested = scraper.get_title(response)
        assert expected == tested

    def test_get_author(self, scraper, response):
        expected = u"AnCing Huang"
        tested = scraper.get_author(response)
        assert expected == tested

    def test_get_thumbnail(self, scraper, response):
        expected = u'https://i.ytimg.com/vi/rXtLH4MJ8u8/hqdefault.jpg'
        tested = scraper.get_thumbnail(response)
        assert expected <= tested

    def test_get_timestamp(self, scraper, response):
        expected = 1429181239
        tested = scraper.get_timestamp(response)
        assert expected == tested

    def test_get_content(self, scraper, response):
        expected = u'description test'
        tested = scraper.get_content(response)
        assert expected == tested

    def test_get_viewCount(self, scraper, response):
        expected = 7
        tested = scraper.get_viewCount(response)
        assert expected <= tested

    def test_get_likeCount(self, scraper, response):
        expected = 0
        tested = scraper.get_likeCount(response)
        assert expected == tested

    def test_get_dislikeCount(self, scraper, response):
        expected = 0
        tested = scraper.get_dislikeCount(response)
        assert expected == tested

    def test_get_commentCount(self, scraper, response):
        expected = 0
        tested = scraper.get_commentCount(response)
        assert expected == tested

    def test_get_rank(self, scraper, response, monkeypatch):
        import sys
        sys.path.append("../crawler")
        import settings
        from rank import Viral_Ranker
        def mockinit(self):
            self.get_rank = eval("self." + settings.RANK_METHOD.lower())
            self.db = sqlalchemy_()
        from abstract_db import sqlalchemy_
        def mockreturn(self, board_id):
            return 1
        #monkeypatch.setattr(Viral_Ranker, 'get_rank', mockreturn)
        monkeypatch.setattr(sqlalchemy_, '__init__', lambda self: None)
        monkeypatch.setattr(sqlalchemy_, 'get_board_rank', mockreturn)
        monkeypatch.setattr(Viral_Ranker, '__init__', mockinit)
        expected = 10
        tested = scraper.get_rank(response)
        assert expected <= tested

    def test_item_init(self):
        scraper_item = youtube.Youtube_Article_Scraper_Item()
        scraper_item['link'] = ""
        assert scraper_item['link'] == ""
        try:
            scraper_item['link2'] = ""
        except:
            assert True


class Test_Youtube_Board_Scraper(object):

    @pytest.fixture()
    def scraper(self):
        scraper = youtube.Youtube_Board_Scraper()
        return scraper

    @pytest.fixture
    def response(self):
        url = "https://www.youtube.com/user/previa960/videos"
        body = urllib2.urlopen(url).read()
        return HtmlResponse(url=url, body=body)

    def test_get_titles(self, scraper, response):
        expected = u"dudu test"
        tested = scraper.get_titles(response)[0]
        assert expected == tested

    def test_get_links(self, scraper, response):
        expected = "https://www.youtube.com/watch?v=rXtLH4MJ8u8"
        tested = scraper.get_links(response)[0]
        assert expected == tested

    def test_get_items(self, scraper, response):
        expected = {
            'board_id': u'UCcTdO4U7mx_yC8j8eNKCJbg',
            'source': 'Youtube',
            'link': u'https://www.youtube.com/watch?v=rXtLH4MJ8u8',
            'timestamp': 1429166664,
            'title': u'dudu test',
            'enable': True
        }

        tested = scraper.get_items(response)[0]
        tested.pop('next_update_time', None)
        expected_timestamp = expected.pop('timestamp')
        tested_timestamp = tested.pop('timestamp')
        assert expected_timestamp <= tested_timestamp
        assert expected == tested

    def test_item_init(self):
        scraper_item = youtube.Youtube_Board_Scraper_Item()
        scraper_item['link'] = ""
        assert scraper_item['link'] == ""
        try:
            scraper_item['link2'] = ""
        except:
            assert True
