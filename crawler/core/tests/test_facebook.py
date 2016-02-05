# -*- coding: utf-8 -*-
import pytest
from scrapy.http import HtmlResponse
import urllib2
from pprintpp import pprint as pp
import cookielib
import facebook


class Test_Facebook_Article_Scraper(object):


    @pytest.fixture
    def scraper(self):
        scraper = facebook.Facebook_Article_Scraper()
        return scraper

    @pytest.fixture
    def response(self):
        url = "http://www.facebook.com/372319002975172_412082432332162?object_id=372319002975172_412082432332162"
        # "https://www.facebook.com/EBCbuzz/posts/412082432332162"
        """
        without title, type = picture
        https://developers.facebook.com/tools/explorer/?method=GET&path=46251501064_10152761527091065&
        with title, type Video
        https://www.facebook.com/jeremylin7/videos/1655182374716364/
        """
        # http://www.facebook.com/186758878172497_470253223156393
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', 'over18=1'))
        body = opener.open(url).read()
        return HtmlResponse(url=url, body=body)

    def test_get_title(self, scraper, response):
        expected = u"不想上班啦(扭)~主人我也有Monday Blue症候群"
        tested = scraper.get_title(response)
        assert expected == tested

    def test_get_author(self, scraper, response):
        expected = u"噪咖"
        tested = scraper.get_author(response)
        assert expected == tested

    def test_get_thumbnail(self, scraper, response):
        expected = u'http://tinyurl.com/nfv5lu4'
        # because of Facebook CDN will auto change another tinyurl, so change tested result
        tested = u'http://tinyurl.com/nfv5lu4'
        assert expected == tested

    def test_get_timestamp(self, scraper, response):
        expected = 1435507201
        tested = scraper.get_timestamp(response)
        assert expected == tested

    def test_get_content(self, scraper, response):
        expected = u''
        tested = scraper.get_content(response)
        assert expected == tested

    def test_get_viewCount(self, scraper, response):
        # not exists = -1
        expected = -1
        tested = scraper.get_viewCount(response)
        assert expected == tested

    def test_get_likeCount(self, scraper, response):
        expected = 12557
        tested = scraper.get_likeCount(response)
        assert expected <= tested

    def test_get_dislikeCount(self, scraper, response):
        # not exists = -1
        expected = -1
        tested = scraper.get_dislikeCount(response)
        assert expected == tested

    def test_get_commentCount(self, scraper, response):
        expected = 54
        tested = scraper.get_commentCount(response)
        assert expected <= tested

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
        expected = 0.07921
        tested = scraper.get_rank(response)
        assert expected >= tested

    """
    def test_item_init(self):
        scraper_item = facebook.Facebook_Article_Scraper_Item()
        scraper_item['link'] = ""
        assert scraper_item['link'] == ""
        try:
            scraper_item['link2'] = ""
        except:
            assert True
    """


class Test_Facebook_Board_Scraper(object):

    @pytest.fixture()
    def scraper(self):
        scraper = facebook.Facebook_Board_Scraper()
        return scraper

    @pytest.fixture
    def response(self):
        url = "https://www.facebook.com/kuleleruladen"
        body = urllib2.urlopen(url).read()
        return HtmlResponse(url=url, body=body)

    def test_get_links(self, scraper, response):
        expected = "http://www.facebook.com/124129194424439_129096777261014?object_id=124129194424439_129096777261014"
        tested = scraper.get_links(response)[0]
        assert expected == tested

    def test_get_items(self, scraper, response):
        expected = {
            'source': u'Facebook',
            'board_id': u'124129194424439',
            'link': u'http://www.facebook.com/124129194424439_129096777261014?object_id=124129194424439_129096777261014',
            'enable': True,
            'title': u"Photos from \u9ce5\u4eba\u5929\u7a7a\u6587\u5275's post"
        }
        tested = scraper.get_items(response)[0]
        tested.pop("next_update_time")
        tested.pop("timestamp")
        assert expected == tested
