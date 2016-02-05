# -*- coding: utf-8 -*-
from core.abstract_db import *


class Scraper_Error_Handler(object):

    def __init__(self):
        self.db = sqlalchemy_()

    def process_item_error(self, response):
        self.db.set_link_to_disable(response)
