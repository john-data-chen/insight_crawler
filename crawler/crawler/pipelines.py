# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pprintpp import pprint as pp
from core.abstract_db import *
import time
import json
import settings
import boto3
from elasticsearch import Elasticsearch

class CrawlerPipeline(object):
    def open_spider(self, spider):
        self.db = sqlalchemy_()

    def process_item(self, item, spider):
        if spider.crawling_type == "article":
            #pp(item)
            _dict = {}
            for k, v in item.items():
                if 'Count' in k:
                    _dict[k] = v
            _dict['timestamp'] = time.time()
            _dict['link'] = item['link']
            _dict['rank'] = item['rank']
            _dict['board_id'] = item['board_id']
            _dict['fansCount'] = item['fansCount']
            self.db.insert_stats(_dict)
            item.pop("fansCount", None)
            self.db.insert_post(item)
            self.db.update_next_update_time(item)
        else:
            self.db.insert_link(item)
        return item

    def close_spider(self, spider):
        pass

class CloudSearchPipeline(object):

    def process_item(self, item, spider):
        if spider.crawling_type == "article":
        #settings.CloudSearch_Doc_Url
        #if 'content' in item:
            endpoint_url = settings.CloudSearch_Doc_Endpoint
            client = boto3.client('cloudsearchdomain',  endpoint_url = endpoint_url)
            f = [
                  {
                    "id": item["link"],
                    "type": "add",
                    "fields": {
                        "author": item["author"],
                        "source": item["source"],
                        "board": item["board"],
                        "board_id": item["board_id"],
                        "title": item["title"],
                        "content": item["content"],
                        "timestamp": item["timestamp"],
                        "link": item["link"],
                        "thumbnail": item["thumbnail"],
                        "rank": item["rank"],
                        "like_count": item["likeCount"],
                        "dislike_count": item["dislikeCount"],
                        "comment_count": item["commentCount"],
                        "share_count": item["shareCount"],
                        "view_count": item["viewCount"]
                    }
                  }
            ]
            jdoc = json.dumps(f)
            try:
                response = client.upload_documents(documents=jdoc, contentType='application/json')
            except Exception,e:
                print e
        return item


class ElasticsearchPipeline(object):
    def open_spider(self, spider):
        es = Elasticsearch([
            {'host': settings.ElasticSearch_HOST,
             'port': settings.ElasticSearch_PORT}
        ])
        self.es = es

    def process_item(self, item, spider):
        setdata = self.es.index(
            index = settings.ElasticSearch_INDEX,
            doc_type = settings.ElasticSearch_DOC_TYPE,
            id = item['link'],
            body = dict(item)
        )
        pp(setdata)

    def close_spider(self, spider):
        pass
