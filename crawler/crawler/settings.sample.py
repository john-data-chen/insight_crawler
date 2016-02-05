# -*- coding: utf-8 -*-

# Scrapy settings for crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawler'

MODE = ""
REDIS_HOST = ""
REDIS_PORT = 9000

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

DOWNLOAD_DELAY = 0.5

MEMDEBUG_ENABLED = True
MEMUSAGE_LIMIT_MB = 50

CLOSESPIDER_TIMEOUT = 600
DOWNLOAD_TIMEOUT = 10

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler (+http://www.yourdomain.com)'
ITEM_PIPELINES = {
    'crawler.pipelines.CrawlerPipeline': 1,
    #'crawler.pipelines.CloudSearchPipeline': 2
}

EXTENSIONS = {
  'scrapy.extensions.closespider.CloseSpider': 20
}

DOWNLOADER_MIDDLEWARES = {
  'scrapy.contrib.downloadermiddleware.downloadtimeout.DownloadTimeoutMiddleware': 10
}

# CloudSearch Doc End-Point
CloudSearch_Doc_Endpoint = ''

# ELASTICSEARCH
ElasticSearch_HOST = ''
ElasticSearch_PORT = 9200
ElasticSearch_INDEX = ''
ElasticSearch_DOC_TYPE = ''

# VIRAL_RANK
RANK_METHOD = "BUZZFEED_RANK"

# CRAWLER
# CRAWLER_ID: [0:], CRAWLER_COUNT:[1:]
CRAWLER_ID = 0
CRAWLER_COUNT = 1

# Scheduler
SCHEDULE_METHOD = 'fix_scheduler'

# YT
YT_API_KEY = "__YT_API_KEY__"

# FB
FB_APP_ID = "__FB_APP_ID__"
FB_APP_SECRET = "__FB_APP_SECRET__"

# Database
DB_CONNECTOR = 'mysql+pymysql'
DB_HOST = ''
DB_PORT = '3306'
DB_DATABASE = 'testdb'
DB_ID = 'root'
DB_PW = 'password'
DB_DRIVE = "%s//%s:%s@%s:%s/%s?charset=utf8" %(DB_CONNECTOR, DB_ID, DB_PW, DB_HOST, DB_PORT, DB_DATABASE)


