# -*- coding: utf-8 -*-
import sys
sys.path.append("../crawler")
from crawler import settings
from scheduler import Scheduler

class article_scheduler(object):

    def __init__(self):
        scheduler = Scheduler()
        self.scheduler = eval("scheduler." + settings.SCHEDULE_METHOD +"")

    def get_next_update_time(self, post):
        return self.scheduler(post)


if __name__ == '__main__':
    fixed_time = 1437283759 - 11*3600
    post = {'timestamp': fixed_time}
    tmp = article_scheduler()
    next_update_time = tmp.get_next_update_time(post)
    print post['timestamp']
    import time
    now = time.time()
    print (next_update_time - now) / 60

