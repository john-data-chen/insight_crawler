# -*- coding: utf-8 -*-
from dateutil import parser
import calendar
import urllib2
import json
from scrapy.item import Item, Field
from scraper import Scraper_Base
import requests
from facepy import GraphAPI
import tinyurl
import re
import time
from core.abstract_db import *
from crawler import settings
from rank import Viral_Ranker


class Facebook_Article_Scraper(Scraper_Base):

    def login_url(self):
        return ("https://www.facebook.com")

    def login_form(self):
        return {'yes': 'yes'}

    def check_login_response(self, response):
        return "self.initialized()"

    def login(self, response):
        return "FormRequest.from_response(response, formdata=%s,\
                callback=self.check_login_response) " % str(self.login_form())

    def __init__(self):
        self.url = None
        self.stats = None
        self.app_id = settings.FB_APP_ID
        self.app_secret = settings.FB_APP_SECRET
        self.access_token = self._get_access_token(self.app_id, self.app_secret)
        Scraper_Base.__init__(self)

    def _get_access_token(self, app_id, app_secret):
        # https://github.com/jgorset/facepy
        # http://stackoverflow.com/questions/3058723/programmatically-getting- \
        #  an-access-token-for-using-the-facebook-graph-api
        payload = {'grant_type': 'client_credentials', 'client_id': app_id, 'client_secret': app_secret}
        file = requests.post('https://graph.facebook.com/oauth/access_token?', params = payload)
        #print file.text #to test what the FB api responded with
        result = file.text.split("=")[1]
        #print file.text #to test the TOKEN
        return result

    def _get_object_id(self, response):
        # http://www.facebook.com/372319002975172_412082432332162?object_id=372319002975172_412082432332162
        get_object_id = response.url.split("=")[-1]
        return get_object_id

    def _get_post(self, response):
        if self.url != response.url:
            get_object_id = self._get_object_id(response)
            graph = GraphAPI(self.access_token)
            # /posts?fields=full_picture,caption,message,id,object_id,picture,from,type,name,description,shares&limit=3
            query_str = "?fields=created_time,full_picture,caption,message,id,status_type,object_id,picture,from,type,name,description,shares&limit=3"
            post = graph.get(get_object_id + query_str)
            self.post = post
            self.url = response.url
            self.fansCount =  self._get_fansCount(response)
        return self.post

    def get_source(self, response):
        return u"Facebook"

    def get_author(self, response):
        post = self._get_post(response)
        if 'from' in post and 'name' in post['from']:
            return post['from']['name']
        return u""

    def get_board_id(self, response):
        post = self._get_post(response)
        if 'from' in post and 'id' in post['from']:
            return post['from']['id']
        return u""

    def get_board(self, response):
        post = self._get_post(response)
        if 'from' in post and 'name' in post['from']:
            return post['from']['name']
        return u""

    def get_title(self, response):
        post = self._get_post(response)
        if 'name' in post:
            return post['name']
        if 'message' in post:
            return post['message'][:30]
        if post['type'] == 'video':
            return "Video Sharing"
        if post['type'] == 'picture':
            return "Picture Sharing"
        return "Link sharing"

    def get_post_type(self, response):
        """
        status_type: enum{mobile_status_update, created_note, added_photos,
                          added_video, shared_story, created_group,
                          created_event, wall_post, app_created_story,
                          published_story, tagged_in_photo, approved_friend}
        type: enum{link, status, photo, video, offer}
        """

        post = self._get_post(response)
        if post['status_type'] == "added_video":
            return u"added_video"
        if post['status_type'] == "added_photos":
            return u"added_photos"

        prefix = u""
        if post['status_type'] == 'shared_story':
            prefix = u"share_"
        return prefix + post['type']

    def get_link(self, response):
        #post = self._get_post(response)
        #return post['link']
        # return tinyurl.create_one(post['link'])
        #get_object_id = self._get_object_id(response)
        #return "http://www.facebook.com/" + get_object_id
        try:
            url = response.request.meta['redirect_urls']
        except Exception as e:
            url = response.url
            print str(e)

        return url

    def get_description(self, response):
        post = self._get_post(response)
        if 'message' in post:
            return post['message']
        return u""

    def get_thumbnail(self, response):
        post = self._get_post(response)
        if 'full_picture' in post:
            return tinyurl.create_one(post['full_picture'])
        if 'picture' in post:
            return tinyurl.create_one(post['picture'])
        return u""

    def get_content(self, response):
        post = self._get_post(response)
        if 'description' in post:
            return post['description']
        else:
            return u""

    def get_timestamp(self, response):
        post = self._get_post(response)
        upload_date = post['created_time']
        return calendar.timegm(parser.parse(upload_date).timetuple())

    def get_viewCount(self, response):
        return -1

    def get_likeCount(self, response):
        # To-Do Use api /likes?summary=1&limit=0 instead of web scraping
        if 'UFIController' in response.body:
            UFIController = response.body.split("UFIController")
            if "commentcount" in UFIController[1]:
                like_section = UFIController[1].split('likecountreduced')[0][-20:]
                likeCount = int(re.findall(r'\d+', like_section)[0])
                return likeCount
        return 0

    def get_dislikeCount(self, response):
        return -1

    def get_commentCount(self, response):
        # TO-DO: Use api instead of web scraping post-id/comments?summary=1&limit=0
        if 'UFIController' in response.body:
            UFIController = response.body.split("UFIController")
            if "commentcount" in UFIController[1]:
                comment_section = UFIController[1].split('commentcount')
                commentCount = int(re.findall(r'\d+', comment_section[1])[0])
                return commentCount
        return 0

    def get_shareCount(self, response):
        post = self._get_post(response)
        if 'shares' in post:
            return post['shares']['count']
        return 0

    def get_fansCount(self, response):
        return self.fansCount

    def get_rank(self, response):
        stats = {}
        stats['board_id'] = self.get_board_id(response)
        stats['likeCount'] = self.get_likeCount(response)
        stats['dislikeCount'] = self.get_dislikeCount(response)
        stats['viewCount'] = self.get_viewCount(response)
        stats['shareCount'] = self.get_shareCount(response)
        stats['commentCount'] = self.get_commentCount(response)
        stats['fansCount'] = self.fansCount
        if stats['fansCount'] == 0:
            stats['fansCount'] = 1
        viral_ranker = Viral_Ranker()
        return viral_ranker.get_rank(stats)

    def _get_fansCount(self, response):
        page_id = response.url.split("object_id=")[1].split("_")[0]
        graph = GraphAPI(self.access_token)
        query_str = "?fields=likes"
        res = graph.get(page_id + query_str)
        return int(res["likes"])


    def get_location(self, response):
        return u""


class Facebook_Board_Scraper(Scraper_Base):

    def login_url(self):
        return ("https://www.facebook.com")

    def login_form(self):
        return {'yes': 'yes'}

    def check_login_response(self, response):
        return "self.initialized()"

    def login(self, response):
        return "FormRequest.from_response(response, formdata=%s,\
                callback=self.check_login_response) " % str(self.login_form())

    def __init__(self):
        self.url = None
        self.stats = None
        self.app_id = settings.FB_APP_ID
        self.app_secret = settings.FB_APP_SECRET
        Scraper_Base.__init__(self)

    def _get_access_token(self, app_id, app_secret):
        # https://github.com/jgorset/facepy
        # http://stackoverflow.com/questions/3058723/programmatically-getting- \
        #  an-access-token-for-using-the-facebook-graph-api
        payload = {'grant_type': 'client_credentials', 'client_id': app_id, 'client_secret': app_secret}
        file = requests.post('https://graph.facebook.com/oauth/access_token?', params = payload)
        #print file.text #to test what the FB api responded with
        result = file.text.split("=")[1]
        #print file.text #to test the TOKEN
        return result

    def get_board_id(self, response):
        get_object_id = self._get_object_id(response)
        access_token = self._get_access_token(self.app_id, self.app_secret)
        graph = GraphAPI(access_token)
        board = graph.get(get_object_id)
        return board["id"]

    def get_source(self, response):
        return u"Facebook"

    def allowed_domains(self):
        return ["facebook.com"]

    def _get_object_id(self, response):
        object_id = ""
        try:
            #object_id = response.url.replace("https://www.facebook.com/", "").replace("?fref=ts","")
            if 'timeline' in response.url:
                # https://www.facebook.com/%E5%BD%AD%E8%8F%AF%E5%B9%B9-185964904840660/timeline/
                object_id = response.url.split('-')[-1].split('/')[0]
            elif "-" in response.url:
                # https://www.facebook.com/Viral-Thread-363765800431935
                import re
                object_id = re.sub("[^0-9]", "", response.url.split('-')[-1])
            elif "?" in response.url:
                # https://www.facebook.com/news.ebc?fref=ts
                object_id = response.url.split("/")[-1].split("?")[-1]
            elif response.url.count("/") == 3:
                # https://www.facebook.com/news.ebc
                object_id = response.url.split("/")[-1].split("?")[-1]
            if object_id.isdigit():
                return object_id
            #if "fb://page" in response.body:
            #!object_id = response.body.split("content=\"fb://page/")[1].split("\"")[0]
            #else:
            if "UserActionHistory" in response.body:
                """
                'Logger"],["ScriptPath","set",[],["XPagesProfileTimelineController","9e7dd28a",{"imp_id":"39a4fa0f"," \
                 entity_id":"232633627068"}],[]],["UserActionHistory"],["ScriptPathLogger","startLogging",[],[],[]],["TimeSpen '
                """
                s = response.body.split("entity_id")[1][:30]
                import re
                object_id = re.match('.*?(\d+)', s).group(1)
                if object_id.isdigit():
                    return object_id
        except Exception as e:
            import logging
            logging.error("Get facebook object id error:" + response.url)
            print str(e)
            import time
            time.sleep(10)
            object_id = ""
        return ""

    def _get_posts(self, response):
        if self.url != response.url:
            object_id = self._get_object_id(response)
            access_token = self._get_access_token(self.app_id, self.app_secret)
            graph = GraphAPI(access_token)
            posts = graph.get(object_id + "/posts?fields=name,created_time")
            self.posts = posts
            self.url = response.url
        return self.posts

    def get_titles(self, response):
        posts = self._get_posts(response)
        titles = []
        try:
            for post in posts['data']:
                if 'name' in post:
                    titles.append(post['name'])
                else:
                    titles.append('')
        except Exception as e:
            from pprintpp import pprint as pp
            pp(response.url)
            print e.message
            time.sleep(10)
        return titles

    def get_next_update_time(self, response):
        return int(time.time())

    def get_links(self, response):
        posts = self._get_posts(response)
        links = []
        for post in posts['data']:
            link = "http://www.facebook.com/%s?object_id=%s" % (post['id'], post['id'])
            links.append(link)
        return links

    def get_timestamps(self, response):
        posts = self._get_posts(response)
        timestamps = []
        for post in posts['data']:
            datetime = post['created_time']
            timestamp = calendar.timegm(parser.parse(datetime).timetuple())
            timestamps.append(timestamp)
        return timestamps

    def get_enable(self, response):
        return True


class Facebook_Board_Scraper_Item(Item):
    class_name = "Facebook_Board_Scraper"
    scraper_item = Scraper_Base()
    exec(scraper_item._get_item_definition(class_name))


class Facebook_Article_Scraper_Item(Item):
    def __setitem__(self, key, value):
        if key not in self.fields:
            self.fields[key] = Field()
        self._values[key] = value
    """
    class_name = "Facebook_Article_Scraper"
    scraper_item = Scraper_Base()
    exec(scraper_item._get_item_definition(class_name))
    """
