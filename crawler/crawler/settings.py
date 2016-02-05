# -*- coding: utf-8 -*-

# Scrapy settings for crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

DOWNLOAD_DELAY = 0.5

MEMDEBUG_ENABLED = True
MEMUSAGE_LIMIT_MB = 50

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler (+http://www.yourdomain.com)'
ITEM_PIPELINES = {
    'crawler.pipelines.CrawlerPipeline': 1,
    'crawler.pipelines.CloudSearchPipeline': 2
}


# CloudSearch Doc End-Point
CloudSearch_Doc_Endpoint = 'http://doc-insight-ehiw5akc6kyu4w47vekmzsuwkm.ap-northeast-1.cloudsearch.amazonaws.com'

# VIRAL_RANK
RANK_METHOD = "BUZZFEED_RANK"

# CRAWLER
# CRAWLER_ID: [0:], CRAWLER_COUNT:[1:]
CRAWLER_ID = 0
CRAWLER_COUNT = 1

# Scheduler
SCHEDULE_METHOD = 'fix_scheduler'

# YT
YT_API_KEY = "AIzaSyAvCAGoX96OQexg5NsJXsVPA9zR9sogeVc"

# FB
FB_APP_ID = "543834309042477"
FB_APP_SECRET = "564457956feff7c664825bd6d0e0ef21"

# Database
DB_CONNECTOR = 'mysql+pymysql'
DB_HOST = 'insight-rds.c4dj8aczgbso.ap-northeast-1.rds.amazonaws.com'
DB_PORT = '3306'
DB_DATABASE = 'debugonly'
DB_ID = 'root'
DB_PW = 'testlalatest'
DB_DRIVE = "%s//%s:%s@%s:%s/%s?charset=utf8" %(DB_CONNECTOR, DB_ID, DB_PW, DB_HOST, DB_PORT, DB_DATABASE)
