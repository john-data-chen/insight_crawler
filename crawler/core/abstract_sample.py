# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, Unicode
from sqlalchemy import Column, Integer, String, Text, DateTime, Table
# from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.engine import reflection
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.expression import *
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.exc import DatabaseError
import time
from sqlalchemy.dialects.mysql import MEDIUMTEXT, TINYINT
import hashlib
from abstract_class import *


class Sample_data(object):

    def get_ptt_board_sample(self):
        gossip = {'source': 'Ptt', 'board': 'Gossiping', 'board_id':'Gossiping',
                'link': 'https://www.ptt.cc/bbs/Gossiping/index.html',
                'fansCount': 100000,'enable':1}
        baseball = {'source': 'Ptt', 'board': 'Baseball', 'board_id':'Baseball',
                  'link': 'https://www.ptt.cc/bbs/Baseball/index.html',
                    'fansCount': 30000,  'enable':1}
        hatepolitics = {'source': 'Ptt', 'board': 'HatePolitics', 'board_id':'HatePolitics',
                    'link': 'https://www.ptt.cc/bbs/HatePolitics/index.html',
                    'fansCount': 35500, 'enable':1}
        sex = {'source': 'Ptt', 'board': 'Sex', 'board_id':'Sex',
               'link': 'https://www.ptt.cc/bbs/sex/index.html',
                 'fansCount': 55000, 'enable':1}
        WomenTalk = {'source': 'Ptt', 'board': 'WomenTalk', 'board_id':'WomenTalk',
                'link': 'https://www.ptt.cc/bbs/WomenTalk/index.html',
                     'fansCount': 27000, 'enable':1}
        Joke = {'source': 'Ptt', 'board': 'Joke', 'board_id':'Joke',
                'link': 'https://www.ptt.cc/bbs/joke/index.html',
                'fansCount': 24000, 'enable':1}
        Boy_Girl = {'source': 'Ptt', 'board': 'Boy-Girl', 'board_id':'Boy-Girl',
                'link': 'https://www.ptt.cc/bbs/Boy-Girl/index.html',
                    'fansCount': 33000, 'enable':1}

        tmps = [gossip, baseball, hatepolitics, sex, WomenTalk, Joke, Boy_Girl]
        return tmps

    def get_fb_board_sample(self):
        tmps = [
            { 'board': u'五月天阿信', 'board_id':'Facebook_211037402285285',
                'link': 'https://www.facebook.com/ashin555'},
            { 'board': u'TEEPR 趣味新聞', 'board_id':'Facebook_1433215316907826',
                'link': 'https://www.facebook.com/teepr'},
            { 'board': u'TEEPR 趣味影片', 'board_id':'Facebook_671746552903006',
                'link': 'https://www.facebook.com/TEEPRVideo'},
            { 'board': u'TEEPR 驚奇新聞', 'board_id':'Facebook_1031526020207033',
                'link': 'https://www.facebook.com/teepromg'},
            { 'board': u'卡卡洛普★宅宅新聞', 'board_id':'Facebook_295855559809',
                'link': 'https://www.facebook.com/kakalopo'},
            { 'board': u'卡提諾論壇｜CK101.COM', 'board_id':'Facebook_206606272737485',
                'link': 'https://www.facebook.com/ck101fans'},
            { 'board': u'卡提諾正妹抱報', 'board_id':'Facebook_480994675249305',
                'link': 'https://www.facebook.com/ck101beauty'},
            { 'board': u'卡提諾正妹抱報加強團3.0', 'board_id':'Facebook_719367321481184',
                'link': 'https://www.facebook.com/ck101beauty3.0'},
            { 'board': 'Giga Circle', 'board_id':'Facebook_387434928062824',
                'link': 'https://www.facebook.com/gigacircle'},
            { 'board': u'LIFE 生活網', 'board_id':'Facebook_316747355036910',
                'link': 'https://www.facebook.com/LIFE.com.tw'},
            { 'board': 'Mobile01', 'board_id':'Facebook_189979853379',
                'link': 'https://www.facebook.com/TheMobile01'},
            { 'board': 'Buzzhand', 'board_id':'Facebook_1458700344364224',
                'link': 'https://www.facebook.com/BuzzHandCom'},
            { 'board': 'Juksy', 'board_id':'Facebook_195769958936',
                'link': 'https://www.facebook.com/juksymag'},
            { 'board': u'niusnews 妞新聞', 'board_id':'Facebook_122152121162647',
                'link': 'https://www.facebook.com/niusnews'},
            { 'board': u'BuzzLife 生活網', 'board_id':'Facebook_1540174832866139',
                'link': 'https://www.facebook.com/Buzzlife.com.tw'},
            { 'board': u'ShareBa分享吧', 'board_id':'Facebook_129654210458157',
                'link': 'https://www.facebook.com/ShareBa.inc'},
            { 'board': 'App01', 'board_id':'Facebook_200171196710695',
                'link': 'https://www.facebook.com/app01fans'},
            { 'board': 'upworthy', 'board_id':'Facebook_354522044588660',
                'link': 'https://www.facebook.com/Upworthy'},
            { 'board': 'buzzfeed', 'board_id':'Facebook_21898300328',
                'link': 'https://www.facebook.com/BuzzFeed'},
            { 'board': '女人迷', 'board_id':'Facebook_184899118190398',
                'link': 'https://www.facebook.com/womany.net'},
            { 'board': 'China Times (中時電子報)', 'board_id':'Facebook_188311137478',
                'link': 'https://www.facebook.com/CTfans'},
            { 'board': '蘋果日報', 'board_id':'Facebook_232633627068',
                'link': 'https://www.facebook.com/appledaily.tw'},
            { 'board': '蘋果日報即時新聞', 'board_id':'Facebook_352962731493606',
                'link': 'https://www.facebook.com/apple.realtimenews'},
            { 'board': '自由時報', 'board_id':'Facebook_394896373929368',
                'link': 'https://www.facebook.com/m.ltn.tw'},
            { 'board': 'ETtoday新聞雲', 'board_id':'Facebook_242305665805605',
                'link': 'https://www.facebook.com/ETtoday'},
            { 'board': 'ETtoday美女雲', 'board_id':'Facebook_260648057386834',
                'link': 'https://www.facebook.com/ETtodayBEAUTY'},
            { 'board': 'ETtoday寵物雲', 'board_id':'Facebook_160915837329440',
                'link': 'https://www.facebook.com/ETtodayPETS'},
            { 'board': 'ETtoday分享雲', 'board_id':'Facebook_238008506256087',
                'link': 'https://www.facebook.com/ETtodaySHARE'},
            { 'board': 'udn.com 聯合新聞網', 'board_id':'Facebook_241284961029',
                'link': 'https://www.facebook.com/myudn'},
            { 'board': 'PTT01', 'board_id':'Facebook_1724597141099774',
                'link': 'https://www.facebook.com/ptt01s'},
            { 'board': 'PopDaily 波波黛莉的異想世', 'board_id':'Facebook_445164788956922',
                'link': 'https://www.facebook.com/PopDaliyMag'},
            {'link':'https://www.facebook.com/OfficialMaviKocaeliVideo'},
            {'link':'https://www.facebook.com/videoincredibilidelweb'},
            {'link':'https://www.facebook.com/Liveleak.Official'},
            {'link':'https://www.facebook.com/Innamagg'},
            {'link':'https://www.facebook.com/fansofvines'},
            {'link':'https://www.facebook.com/BuzzFeed'},
            {'link':'https://www.facebook.com/BuzzFeedVideo'},
            {'link':'https://www.facebook.com/BuzzFeedBlue'},
            {'link':'https://www.facebook.com/thisgroupofpeople'},
            {'link':'https://www.facebook.com/TaiwanTalentShow?fref=ts'},
            {'link':'https://www.facebook.com/KATOTAKA2.0?fref=ts'},
            {'link':'https://www.facebook.com/BestofVines?fref=ts'},
            {'link':'https://www.facebook.com/lessonsfrommovies?fref=ts'},
            {'link':'https://www.facebook.com/SuperFunPic?fref=ts'},
            {'link':'https://www.facebook.com/ideapit?fref=ts'},
            {'link':'https://www.facebook.com/myoops?fref=ts'},
            {'link':'https://www.facebook.com/wunienjen?fref=ts'},
            {'link':'https://www.facebook.com/tsaiingwen?fref=ts'},
            {'link':'https://www.facebook.com/ChuChuPepper'},
            {'link':'https://www.facebook.com/kaifulee?fref=ts'},
            {'link':'https://www.facebook.com/CEO.HSIEH?fref=ts'},
            {'link':'https://www.facebook.com/MaYingjeou?fref=ts'},
            {'link':'https://www.facebook.com/hoo.jcai?fref=ts'},
            {'link':'https://www.facebook.com/jay?fref=ts'},
            {'link':'https://www.facebook.com/jackywuofficial?fref=ts'},
            {'link':'https://www.facebook.com/swhite523?fref=ts'},
            {'link':'https://www.facebook.com/IsShow?fref=ts'},
            {'link':'https://www.facebook.com/amber.fans?fref=ts'},
            {'link':'https://www.facebook.com/eagleBii?fref=ts'},
            {'link':'https://www.facebook.com/officialsistar?fref=ts'},
            {'link':'https://www.facebook.com/boommini?hc_location=ufi'},
            {'link':'https://www.facebook.com/ili19930831official?fref=ts'},
            {'link':'https://www.facebook.com/bc.ashi?fref=ts'},
            {'link':'https://www.facebook.com/DoctorKoWJ?fref=ts'},
            {'link':'https://www.facebook.com/Beckham?fref=nf'},
            {'link':'https://www.facebook.com/barackobama?fref=nf'},
            {'link':'https://www.facebook.com/officialtomcruise?fref=nf'},
            {'link':'https://www.facebook.com/pitbull?fref=nf'},
            {'link':'https://www.facebook.com/sandymandy0731?fref=ts'},
            {'link':'https://www.facebook.com/duncanlindesign?fref=ts'},
            {'link':'https://www.facebook.com/leehom?fref=ts'},
            {'link':'https://www.facebook.com/SoniaSuiOfficialFanPage?fref=ts'},
            {'link':'https://www.facebook.com/WithGaLoveTaiwan?fref=ts'},
            {'link':'https://www.facebook.com/pages/%E5%B0%8FS-%E5%BE%90%E7%86%99%E5%A8%A3/1509106909358665?fref=ts'},
            {'link':'https://www.facebook.com/jamsclub?fref=ts'},
            {'link':'https://www.facebook.com/pages/%E4%B9%9D%E6%8A%8A%E5%88%80-Giddens-Ko/122355981186846?fref=ts'},
            {'link':'https://www.facebook.com/niniouyang8?fref=ts'},
            {'link':'https://www.facebook.com/GEORGECHANG2014?fref=ts'},
            {'link':'https://www.facebook.com/vanness?fref=ts'},
            {'link':'https://www.facebook.com/ciaociaorose?fref=ts'},
            {'link':'https://www.facebook.com/kikuChen?fref=ts'},
            {'link':'https://www.facebook.com/DreamGirlsPuff?fref=ts'},
            {'link':'https://www.facebook.com/gogogoeball?fref=ts'},
            {'link':'https://www.facebook.com/tsengwanting?fref=ts'},
            {'link':'https://www.facebook.com/aaronyanmusic?fref=ts'},
            {'link':'https://www.facebook.com/llchu?ref=ts&fref=ts'},
            {'link':'https://www.facebook.com/waitforyou77?fref=ts'},
            {'link':'https://www.facebook.com/houwenyongpage?fref=ts'},
            {'link':'https://www.facebook.com/Hopelinfansclub?fref=ts'},
            {'link':'https://www.facebook.com/Anchor.haiyin?fref=ts'},
            {'link':'https://www.facebook.com/pages/A-Lin-920/1511096155841274?fref=ts'},
            {'link':'https://www.facebook.com/gracetw1988?fref=ts'},
            {'link':'https://www.facebook.com/93jqq?fref=ts'},
            {'link':'https://www.facebook.com/amogood?fref=ts'},
            {'link':'https://www.facebook.com/bbctrad?fref=ts'},
            {'link':'https://www.facebook.com/bbcnews?fref=ts'},
            {'link':'https://www.facebook.com/cnn?fref=ts'},
            {'link':'https://www.facebook.com/HuffingtonPost'},
            {'link':'https://www.facebook.com/CCTV.CH'},
            {'link':'https://www.facebook.com/natgeo'},
            {'link':'https://www.facebook.com/BuzzFeedNews'},
            {'link':'https://www.facebook.com/theguardian'},
            {'link':'https://www.facebook.com/techcrunch?ref=ts&fref=ts'},
            {'link':'https://www.facebook.com/NASA?fref=nf'},
            {'link':'https://www.facebook.com/bbcworldnews'},
            {'link':'https://www.facebook.com/mlb'},
            {'link':'https://www.facebook.com/nba?fref=ts'},
            {'link':'https://www.facebook.com/uefacom?fref=ts'},
            {'link':'https://www.facebook.com/LPGA?fref=ts'},
            {'link':'https://www.facebook.com/tennis?fref=ts'},
            {'link':'https://www.facebook.com/pttcitizen1985?fref=ts'},
            {'link':'https://www.facebook.com/lslandnationyouth'},
            {'link':'https://www.facebook.com/Geekfirm'},
            {'link':'https://www.facebook.com/koreastardaily'},
            {'link':'https://www.facebook.com/kpopn'},
            {'link':'https://www.facebook.com/koreaboo'},
            {'link':'https://www.facebook.com/sbsnow'},
            {'link':'https://www.facebook.com/chocokoreandrama'},
            {'link':'https://www.facebook.com/nownews'}
        ]

        return tmps

    def get_yt_board_sample(self):
        tmps = [
                {'source': 'Youtube', 'board': 'udn tv', 'board_id':'Youtube_udntv',
                 'link': 'https://www.youtube.com/user/udntv/videos', 'enable':1},
                {'source': 'Youtube', 'board': '三立新聞台 CH54', 'board_id':'Youtube_setnews159',
                 'link': 'https://www.youtube.com/user/setnews159/videos', 'enable':1},
                {'source': 'Youtube', 'board': 'TVBS影音直播', 'board_id':'Youtube_UCrILBnNNZjnlMjpR_XF2OoQ',
                 'link': 'https://www.youtube.com/channel/UCrILBnNNZjnlMjpR_XF2OoQ/videos', 'enable':1},
                {'source': 'Youtube', 'board': '中天新聞 CH52', 'board_id':'Youtube_ctitvnews52',
                 'link': 'https://www.youtube.com/user/ctitvnews52/videos', 'enable':1},
                {'source': 'Youtube', 'board': 'USTV 非凡電視台', 'board_id':'Youtube_ustv',
                 'link': 'https://www.youtube.com/user/ustv/videos', 'enable':1},
                {'source': 'Youtube', 'board': '中天電視', 'board_id':'Youtube_ctitv',
                 'link': 'https://www.youtube.com/user/ctitv/videos', 'enable':1},
                {'source': 'Youtube', 'board': 'BuzzFeedVideo', 'board_id':'Youtube_BuzzFeedVideo',
                 'link': 'https://www.youtube.com/user/BuzzFeedVideo/videos', 'enable':1},
                {'source': 'Youtube', 'board': u'TEEPR 趣味影片', 'board_id':'Youtube_UCzAOdjLlfyW19t8PtG1f7MA',
                 'link': 'https://www.youtube.com/channel/UCzAOdjLlfyW19t8PtG1f7MA/videos', 'enable':1},
                {'source': 'Youtube', 'board': u'TEEPR 趣味新聞', 'board_id':'Youtube_UCXdRvUovEANz8EZEe67e8Sg',
                 'link': 'https://www.youtube.com/channel/UCXdRvUovEANz8EZEe67e8Sg/videos', 'enable':1},
                {'source': 'Youtube', 'board': 'Rumble Viral', 'board_id':'Youtube_rumbleviral',
                 'link': 'https://www.youtube.com/user/rumbleviral/videos', 'enable':1},
                {'source': 'Youtube', 'board': 'TheFineBros', 'board_id':'Youtube_TheFineBros',
                 'link': 'https://www.youtube.com/user/TheFineBros/videos', 'enable':1},
               ]
        return tmps