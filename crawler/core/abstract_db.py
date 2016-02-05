# -*- coding: utf-8 -*-
import sys
sys.path.append("../crawler")
from sqlalchemy import create_engine, Unicode
from sqlalchemy import Column, Integer, String, Text, DateTime, Table
# from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
# from sqlalchemy.engine import reflection
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.expression import *
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.exc import DatabaseError
import time
#from sqlalchemy.dialects.mysql import MEDIUMTEXT, TINYINT
import hashlib
from abstract_class import Base as Base_Class
from abstract_sample import *
from crawler import settings
from sqlalchemy.exc import ProgrammingError
from sqlalchemy_utils.functions import database_exists
import argparse
from pprintpp import pprint as pp
from article_scheduler import article_scheduler
#from scrapy import log
import requests
from facepy import GraphAPI
import json
import urllib2

Base = Base_Class


def create_database():

    db_drive = '%s://%s:%s@%s:%s/%s?charset=utf8' % (settings.DB_CONNECTOR, settings.DB_ID,
                settings.DB_PW, settings.DB_HOST, settings.DB_PORT,
                settings.DB_DATABASE)

    if database_exists(db_drive):
        print "db:%s already exist" % settings.DB_DATABASE
        return True

    db_drive = '%s://%s:%s@%s:%s/%s?charset=utf8' % (settings.DB_CONNECTOR, settings.DB_ID,
                settings.DB_PW, settings.DB_HOST, settings.DB_PORT, '')
    engine = create_engine(db_drive, encoding='utf-8', echo=True)
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("create database %s" % settings.DB_DATABASE)
    conn.close()


class sqlalchemy_(object):

    def __init__(self):

        # use below command to install driver, do "not" install deb on MySQL site
        # pip install mysql-connector-python --allow-external mysql-connector-python

        db_drive = '%s://%s:%s@%s:%s/%s?charset=utf8' % (settings.DB_CONNECTOR, settings.DB_ID,
                    settings.DB_PW, settings.DB_HOST, settings.DB_PORT,
                    settings.DB_DATABASE)

        if not database_exists(db_drive):
            print """Database %s not exist ! Please initial database setting by
            execute python abstract_db.py --create_db --create_sample_data""" % \
            settings.DB_DATABASE
            import sys
            sys.exit()

        self.engine = create_engine(db_drive, encoding='utf-8', echo=False)

        #if not database_exists(db_drive):
        Base.metadata.create_all(self.engine)

        Session = scoped_session(sessionmaker(bind=self.engine))
        self.session = Session()
        self.scheduler = article_scheduler()

    def insert_post(self, post):
        _posts = self.session.query(Posts).filter_by(link=post['link']).all()
        if len(_posts) > 0:
            print ">>>>>  Delete existed data"
            # Doesn't need to delete just ignore
            self.session.delete(_posts[0])
            #self.session.commit()
        post['description'] = post['description'][:768]
        post['content'] = post['content'][:768]
        self.session.merge(Posts(**post))
        self.session.commit()

    def set_link_to_disable(self, response):
        if 'redirect_urls' in response.request.meta:
            if type(response.request.meta['redirect_urls']) == list:
                error_url = response.request.meta['redirect_urls'][0]
            else:
                error_url = response.url
        else:
            error_url = response.url
        link = self.session.query(Links).filter_by(link=error_url).first()
        if link != None:
            link.enable = False
            self.session.commit()

    def insert_link(self, link):
        # Insert Ignore
        # http://169it.com/tech-python/article-1734263554.html
        # http://stackoverflow.com/questions/2218304/sqlalchemy-insert-ignore
        self.session.execute(Links.__table__.insert().prefix_with('IGNORE'),
             link)
        self.session.commit()
        """
        Approach 1: Delete before Insert
        _link = self.session.query(Links).filter_by(link=link['link']).all()
        if len(_link) > 0:
            print ">>>>>  Delete existed data"
            # Doesn't need to delete just ignore
            # session.delete(_link[0])
        else:
            self.session.merge(Links(**link))
        self.session.commit()
        """
        """
        Approach 2: insert_on_duplicate_key
        TO-DO Using insert_on_duplicate_key instead of insert after delete
        def inert_on_duplicate_key(self, data_dict):
            # http://docs.sqlalchemy.org/en/latest/core/connections.html
            connection = self.engine.connect()
            # result = connection.execute("select username from users")
            #connection.execute(posts.insert(append_string = 'ON DUPLICATE KEY UPDATE link=%s' %s data_dict['link']), input_str)
            connection.execute(links.insert(append_string = "ON DUPLICATE KEY UPDATE source='%s'" %data_dict['source']) , link=data_dict['link'])
            # connection.execute(links.insert(append_string = "ON DUPLICATE KEY UPDATE " ) , link=data_dict['link'])
            # (append_string = 'ON DUPLICATE KEY UPDATE link=%s' %s data_dict['link']), input_str)
            connection.close()

        meta = MetaData()
        posts = Table('Posts', meta,
            Column('id', Integer, primary_key=True, nullable=True, autoincrement=True),
            .....
            )
        links = Table('links', meta,
            Column('id', Integer, primary_key=True, nullable=True, autoincrement=True),
            ....
            )

        @compiles(Insert)
        def append_string(insert, compiler, **kw):
            s = compiler.visit_insert(insert, **kw)
            if 'append_string' in insert.kwargs:
                return s + " " + insert.kwargs['append_string']
            return s
        """

    def insert_stats(self, stats):
        self.session.merge(Stats(**stats))
        self.session.commit()

    def update_board_last_check_time(self, start_urls):
        import time
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        for url in start_urls:
            print url
            _ = self.session.query(Boards).filter(Boards.link == url).\
                                      filter(Boards.enable == 1).\
                                      first()
            if _ != None:
                _.last_check_time = now
                self.session.commit()
            else:
                print "wired ", url

    def update_next_update_time(self, post):
        link = self.session.query(Links).filter(Links.link == post['link'])\
                                        .first()
        if link != None:
            link.next_update_time = self.scheduler.get_next_update_time(post)
            self.session.commit()

    def get_board_fansCount(self, board_id):
        Session = scoped_session(sessionmaker(bind=self.engine))
        session = Session()
        boards = session.query(Boards).filter(Boards.board_id == board_id).all()
        session.close()
        for board in boards:
            _ = board.__dict__
            return _['fansCount']
        return 0

    def start_urls(self, source, crawling_type, crawler_id, crawler_count):
        result = []
        if crawling_type == "Board":
            result = self.query_board_start_url(source, crawler_id, crawler_count)
        elif crawling_type == "Article":
            result = self.query_start_url(source, crawler_id, crawler_count)
        return result

    def query_start_url(self, source, crawler_id, crawler_count):
        now = int(time.time())
        timestamp = int(time.time() - 3600*72)
        Session = scoped_session(sessionmaker(bind=self.engine))
        session = Session()

        links = session.query(Links).filter(Links.source == source)\
                .filter(Links.timestamp >= timestamp)\
                .filter(Links.id % crawler_count == crawler_id)\
                .filter(Links.enable == 1) \
                .filter(Links.next_update_time <= now)\
                .order_by(desc(Links.next_update_time))\
                .limit(30)

        response = []
        count = 0
        for link in links:
            count += 1
            _tmp = link.__dict__
            if _tmp['id'] % crawler_count != (crawler_id):
                continue
            # _tmp.pop('_sa_instance_state', None)
            response.append(_tmp['link'])
        session.close()

        f = open('/tmp/crawler.log', 'a')
        logstr = "\n%s, %s, %s" % (crawler_id, count, now)
        f.write(logstr)
        f.close()

        return response

    def query_board_start_url(self, source, crawler_id, crawler_count):
        Session = scoped_session(sessionmaker(bind=self.engine))
        session = Session()
        boards = session.query(Boards).filter(Boards.source == source)\
                                      .filter(Boards.enable == 1).all()
        response = []
        for board in boards:
            _tmp = board.__dict__
            if _tmp['id'] % crawler_count != (crawler_id):
                continue
            # _tmp.pop('_sa_instance_state', None)
            link = _tmp['link'].split('?')[0]
            response.append(link)
        session.close()
        return response


    ############################################################################
    def get_board_source_by_link(self, link):
        if "www.ptt.cc" in link:
            return "Ptt"

        if "www.facebook.com" in link:
            return "Facebook"

        if "youtube.com" in link:
            return "Youtube"
        return "Not-supported"


    def get_board_id_by_link(self, link):
        if "www.ptt.cc" in link:
            return link.split("/")[-2]
        if "www.facebook.com" in link:
            url = ""
            if 'timeline' in link:
                url = link.split('-')[-1].split('/')[0]
            elif '-' in url:
                # https://www.facebook.com/Viral-Thread-363765800431935
                import re
                url = re.sub("[^0-9]", "", link.split('-')[-1])
            else:
                url = link.split("/")[-1].split("?")[0]

            query_id = url
            access_token = self._get_access_token()
            graph = GraphAPI(access_token)
            board = graph.get(query_id)
            return board["id"]

        if "youtube.com" in link:
            link = link.replace("/videos/", "")
            link = link.replace("/videos", "")
            if "channel" in link:
                return link.replace("https://www.youtube.com/channel/", "")
            elif "user" in link:
                username = link.replace("https://www.youtube.com/user/", "")
                api_key = settings.YT_API_KEY
                api_link = "https://www.googleapis.com/youtube/v3/channels?key=%s&forUsername=%s&part=id" % (
                    api_key, username)
                result = json.load(urllib2.urlopen(api_link))
                return result['items'][0]['id']
            else:
                return ""


    def _get_access_token(self):
        app_id = settings.FB_APP_ID
        app_secret = settings.FB_APP_SECRET
        # https://github.com/jgorset/facepy
        # http://stackoverflow.com/questions/3058723/programmatically-getting- \
        #  an-access-token-for-using-the-facebook-graph-api
        payload = {'grant_type': 'client_credentials', 'client_id': app_id, 'client_secret': app_secret}
        _ = requests.post('https://graph.facebook.com/oauth/access_token?', params=payload)
        # print file.text #to test what the FB api responded with
        result = _.text.split("=")[1]
        # print file.text #to test the TOKEN
        return result

    def get_board_by_link(self, link):

        if "www.ptt.cc" in link:
            return link.split("/")[-2]
        if "www.facebook.com" in link:
            fb_id = self.get_board_id_by_link(link)
            """
            170901143077174
            """
            access_token = self._get_access_token()
            graph = GraphAPI(access_token)
            print ">>", fb_id
            board = graph.get(fb_id)
            return board["name"]

        if "youtube.com" in link:
            channel_id = self.get_board_id_by_link(link)
            api_key = settings.YT_API_KEY
            api_link = "https://www.googleapis.com/youtube/v3/channels?key=%s&id=%s&part=snippet" % (
                api_key, channel_id)
            result = json.load(urllib2.urlopen(api_link))
            board_title = result['items'][0]['snippet']['title']
            return board_title

        return ""

    def get_board_link(self, url, source_type, board_id):
        if source_type == "Ptt":
            return "https://www.ptt.cc/bbs/" + board_id + "/index.html"
        if source_type == "Youtube":
            if "channel" in url:
                return "https://www.youtube.com/channel/" + board_id
            if "user" in url:
                return "https://www.youtube.com/user/" + board_id

        if source_type == "Facebook":
            return "https://www.facebook.com/" + board_id


    def insert_board_by_url(self, url):
        # get sample data
        # get board_data from api
        # insert into database
        try:
            tmp = {}
            tmp["enable"] = 1
            tmp["source"] = self.get_board_source_by_link(url)
            tmp["board"] = self.get_board_by_link(url)
            tmp["board_id"] = self.get_board_id_by_link(url)
            tmp["link"] = self.get_board_link(url, tmp["source"], tmp["board_id"])
        except Exception as e:
            print "error", str(e)
            return ""

        _board = self.session.query(Boards).filter_by(link=tmp['link']).all()
        if len(_board) > 0:
            print ">>>>>  Delete existed data"
        else:
            self.session.merge(Boards(**tmp))
        self.session.commit()

    def insert_ptt_board_sample(self):
        sample_data = Sample_data()
        tmps = sample_data.get_ptt_board_sample()
        for tmp in tmps:
            self.insert_board_by_url(tmp["link"])

    def insert_fb_board_sample(self):
        m = hashlib.md5()
        sample_data = Sample_data()
        tmps = sample_data.get_fb_board_sample()
        for tmp in tmps:
            self.insert_board_by_url(tmp["link"])

    def insert_yt_board_sample(self):
        sample_data = Sample_data()
        tmps = sample_data.get_yt_board_sample()
        for tmp in tmps:
            self.insert_board_by_url(tmp["link"])

    def get_board_rank(self, board_id):
        board = self.session.query(Boards).filter(board_id==board_id).first()
        if board != None:
            return board.rank
        else:
            print '!!!!', "board.rank query error"
        return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-c", "--create_db", help="create database", \
            action="store_true", dest='create_db')
    parser.add_argument("-s", "--insert_sample_data", help="insert sample data", \
            action="store_true", dest='insert_sample_data')
    args = parser.parse_args()

    if args.create_db:
        create_database()
    if args.insert_sample_data:
        db = sqlalchemy_()
        db.insert_ptt_board_sample()
        db.insert_fb_board_sample()
        db.insert_yt_board_sample()

    db = sqlalchemy_()
    #posts = db.session.query(Posts).filter(Posts.source=='Ptt').limit(10)
    now = int(time.time())
    since  = int(time.time() - 3600*24*3)
    posts = db.session.query(func.count(Links.id)).filter(Links.next_update_time<now).filter(Links.next_update_time>since).scalar()
    pp(posts)
    """
    for post in posts:
        print post.__dict__
    """

