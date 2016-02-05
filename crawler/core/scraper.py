# -*- coding: utf-8 -*-
from itertools import izip
import time
from datetime import *
#from datetime import datetime
import datetime
from scrapy.exceptions import IgnoreRequest
from error_handler import Scraper_Error_Handler
import re
from core.abstract_db import *


class Scraper_Base(object):

    def __init__(self, CRAWLER_COUNT='', CRAWLER_ID=''):
        self.CRAWLER_COUNT = CRAWLER_COUNT
        self.CRAWLER_ID = CRAWLER_ID

    def start_urls(self, source, crawling_type, crawler_id, crawler_count):
        db = sqlalchemy_()
        urls = db.start_urls(source, crawling_type, crawler_id, crawler_count)
        if crawling_type == "Board":
            db.update_board_last_check_time(urls)
        return urls

    def _get_item_definition(self, scraper):
        item_class = scraper.split('_')[0].lower()
        exec("from " + item_class + " import " + scraper)
        result = ""
        for field, value in eval(scraper + ".__dict__.items()"):
            if field[0] == "_":
                continue
            if "get_" in field and field != "get_items":
                _field = field.replace("get_", "")
                if field[-1] == 's':
                    _field = _field[:-1]
                # exec(_field + " = Field()")
                result += _field + " = Field()\n"
                if _field == "timestamp":
                    result += "create_time = Field()\n"
        return result

    def parse_all_fields(self, response):

        re_pattern = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)
        key, values = [], []
        if 'Board' in self.__class__.__name__:
            Magic = 500
        else:
            Magic = 1
        for field, value in self.__class__.__dict__.items():
            # print field
            if field[0] == "_":
                continue
            if "get_" in field and field != "get_items":
                # print field, value
                _field = field.replace("get_", "")
                if field[-1] == 's':
                    _field = _field[:-1]
                key.append(_field)
                _values = ""
                # exec("_values = self."+ field + "(response)") in \
                # globals(), locals()
                # exec doesn't overwrite _values
                try:
                    _values = eval("self." + field + "(response)")
                except:
                    import logging
                    logging.error("Error parsing field " + field)
                    raise ValueError("Error parsing field " + field)
                if type(_values) != list:
                    _values = [_values] * Magic
                    # TO-DO use generators to replace Magic
                for idx, _v in enumerate(_values):
                    if type(_v) == unicode:
                        _values[idx] = re_pattern.sub(u'\uFFFD', _v)
                values.append(_values)

                if _field == "timestamp" and 'Board' not in self.__class__.__name__:
                    key.append("create_time")
                    values.append([self.get_create_time(_values[0])])

        # print type(values), values
        field_dict_list = [dict(zip(key, value)) for value in izip(*values)]
        return field_dict_list

    def populate_items(self, key_value_dict_list):
        scraper = self.__class__.__name__
        item_class = scraper.split('_')[0].lower()
        exec("from %s import %s_Item as Scraper_Item" % (item_class, scraper))
        items = []
        for _dict in key_value_dict_list:
            _item = eval("Scraper_Item()")
            # exec('_item = Scraper_Item()')
            for k, v in _dict.items():
                _item[k] = v
            items.append(_item)
        return items

    def get_items(self, response):
        try:
            _items = self.parse_all_fields(response)
            items = self.populate_items(_items)
        except Exception as e:
            print str(e)
            #raise IgnoreRequest()
            return None
        return items

    def get_item(self, response):
        _tmp = None
        try:
            _tmp = self.get_items(response)[0] or None
        except:
            scraper_error_handler = Scraper_Error_Handler()
            scraper_error_handler.process_item_error(response)

        return _tmp

    def get_timestamp(self, response):
        # TO-DO: It seems not work so i have to add get_timestamp to
        # each board_crawler
        return int(time.time())

    def get_create_time(self, timestamp):
        #timestamp = self.get_timestamp(response)
        #time_struct = datetime.fromtimestamp(timestamp)
        #time_struct = time.gmtime(timestamp)
        #return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
        # return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%dT%H:%M:%S')
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
