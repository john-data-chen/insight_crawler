# -*- coding: utf-8 -*-
from dateutil import parser
import calendar
import urllib2
import json
from scrapy.item import Item, Field
from scraper import Scraper_Base
import time
from core.abstract_db import *
from crawler import settings
from rank import Viral_Ranker

class Youtube_Article_Scraper(Scraper_Base):

    def __init__(self):
        self.url = None
        self.stats = None
        Scraper_Base.__init__(self)

    def get_source(self, response):
        return u"Youtube"

    def get_author(self, response):
        data = self._get_data_from_api(response)
        return data['items'][0]['snippet']['channelTitle']

    def get_board_id(self, response):
        data = self._get_data_from_api(response)
        return data['items'][0]['snippet']['channelId']

    def get_board(self, response):
        data = self._get_data_from_api(response)
        return data['items'][0]['snippet']['channelTitle']

    def get_title(self, response):
        data = self._get_data_from_api(response)
        return data['items'][0]['snippet']['title']


    def get_link(self, response):
        if 'redirect_urls' in response.request.meta:
            return response.request.meta['redirect_urls']
        else:
            return response.url
        return response.request.meta['redirect_urls']

    def get_description(self, response):
        return u""

    def get_thumbnail(self, response):
        data = self._get_data_from_api(response)
        return data['items'][0]['snippet']['thumbnails']['high']['url']

    def get_content(self, response):
        data = self._get_data_from_api(response)
        return data['items'][0]['snippet']['description']

    def get_timestamp(self, response):
        data = self._get_data_from_api(response)
        upload_date = data['items'][0]['snippet']['publishedAt']
        return calendar.timegm(parser.parse(upload_date).timetuple())

    def get_viewCount(self, response):
        data = self._get_data_from_api(response)
        return int(data['items'][0]['statistics']['viewCount'])

    def get_likeCount(self, response):
        data = self._get_data_from_api(response)
        return int(data['items'][0]['statistics']['likeCount'])

    def get_dislikeCount(self, response):
        data = self._get_data_from_api(response)
        return int(data['items'][0]['statistics']['dislikeCount'])

    def get_commentCount(self, response):
        data = self._get_data_from_api(response)
        return int(data['items'][0]['statistics']['commentCount'])

    def get_shareCount(self, response):
        data = self._get_data_from_api(response)
        return data["shareCount"]

    def get_fansCount(self, response):
        data = self._get_data_from_api(response)
        return data["fansCount"]

    def _get_shareCount(self, response):
        end_point = "http://api.facebook.com/restserver.php?method=links.getStats&format=json&urls="
        query_url = response.url
        api_link = end_point + query_url
        result = urllib2.urlopen(api_link)
        stats = json.load(result)
        return stats[0]['share_count']

    def _get_fansCount(self, response, board_id):
        end_point = "https://www.googleapis.com/youtube/v3/channels"
        channel_id = board_id
        api_key = settings.YT_API_KEY
        api_link = "%s?id=%s&key=%s&part=statistics" % (end_point, channel_id,
                                                        api_key)
        result = urllib2.urlopen(api_link)
        _ = json.load(result)
        fansCount = int(_["items"][0]["statistics"]["subscriberCount"])
        if fansCount == 0:
            fansCount = 1
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
        return u"video"

    def _get_data_from_api(self, response):
        if self.url is not response.url:
            yid = response.url.replace("https://www.youtube.com/watch?v=", "")
            end_point = "https://www.googleapis.com/youtube/v3/videos"
            api_key = settings.YT_API_KEY
            api_link = "%s?id=%s&key=%s&part=snippet,statistics" % (
                        end_point, yid, api_key)
            result = urllib2.urlopen(api_link)
            stats = json.load(result)
            stats["shareCount"] = self._get_shareCount(response)
            stats["fansCount"] = self._get_fansCount(response, stats['items'][0]['snippet']['channelId'])
            self.stats = stats
            self.url = response.url
        return self.stats


class Youtube_Board_Scraper(Scraper_Base):

    """
    def login_page(self):
        return ("https://www.youtube.com/user/previa960/videos")
    """

    def __init__(self):
        self.url = ""
        self.data = ""
        Scraper_Base.__init__(self)

    def get_board_id(self, response):
        url = response.url.replace("videos", "")
        if "channel" in url:
            """
            https://www.youtube.com/channel/UCrILBnNNZjnlMjpR_XF2OoQ
            https://www.youtube.com/channel/UCrILBnNNZjnlMjpR_XF2OoQ/videos
            """
            return url.replace("https://www.youtube.com/channel/", "").replace("/","")

        elif "user" in url:
            """
            https://www.youtube.com/user/rumbleviral/videos
            """
            username = url.replace("https://www.youtube.com/user/","").replace("/", "")
            api_link = "https://www.googleapis.com/youtube/v3/channels?key=%s&forUsername=%s&part=id" % (settings.YT_API_KEY, username)
            result = json.load(urllib2.urlopen(api_link))
            channel_id = result['items'][0]['id']
            return channel_id
        else:
            return u""

    def get_source(self, response):
        return u"Youtube"

    def allowed_domains(self):
        return ["www.youtube.com"]

    def get_titles(self, response):
        data = self._get_data_from_api(response)
        links = []
        for item in data["items"]:
            links.append(item["snippet"]["title"])

        prefix = ""
        return [prefix + link.strip() for link in links]

    def get_next_update_time(self, response):
        return int(time.time())

    def get_links(self, response):
        data = self._get_data_from_api(response)
        links = []
        for item in data["items"]:
            links.append(item["snippet"]["resourceId"]["videoId"])

        prefix = "https://www.youtube.com/watch?v="
        return [prefix + link.strip() for link in links]

    def get_timestamps(self, response):
        data = self._get_data_from_api(response)
        timestamps = []
        for item in data["items"]:
            datetime = item["snippet"]["publishedAt"]
            timestamp = calendar.timegm(parser.parse(datetime).timetuple())
            timestamps.append(timestamp)

        return timestamps

    def _get_data_from_api(self, response):
        if self.url is not response.url:
            channel_id = self.get_board_id(response)
            # To-Do: You can use one step to get video data instead of two
            # api_link ="https://www.googleapis.com/youtube/v3/search?key=%s&channelId=%s&part=snippet,id&order=date" % (settings.YT_API_KEY, channel_id)
            api_link = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id=%s&key=%s" % (channel_id, settings.YT_API_KEY)
            playlist_id = json.load(urllib2.urlopen(api_link))["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            api_link = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=%s&key=%s" % (playlist_id, settings.YT_API_KEY)
            result = json.load(urllib2.urlopen(api_link))
            self.url = response.url
            self.data = result
        return self.data

    def get_enable(self, response):
        return True


class Youtube_Board_Scraper_Item(Item):
    class_name = "Youtube_Board_Scraper"
    scraper_item = Scraper_Base()
    exec(scraper_item._get_item_definition(class_name))


class Youtube_Article_Scraper_Item(Item):
    class_name = "Youtube_Article_Scraper"
    scraper_item = Scraper_Base()
    exec(scraper_item._get_item_definition(class_name))
