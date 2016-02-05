import time

class Scheduler(object):

    def type_scheduler(self, post):
        pass

    def fix_scheduler(self, post):
        return int(time.time()) + 900

    def rank_scheduler(self, post):
        pass

    def duration_scheduler(self, post):

        now = int(time.time())
        create_time = post['timestamp']
        diff_time = now - create_time

        _1hr = 3600
        _2hr = 3600*2
        _3hr = 3600*3
        _4hr = 3600*4
        _6hr = 3600*6
        _12hr = 3600*12
        _24hr = 3600*24
        _48hr = 3600*48
        _72hr = 3600*72

        print now, create_time, diff_time

        if diff_time < 0:
            # Error case, post from furthre
            raise Exception('Error: Post from further')

        # within 1 hr
        if diff_time < _1hr:
            return now + 360

        # within 2 hr
        if diff_time < _2hr:
            return now + 900

        # within 6 hr
        if diff_time < _6hr:
            return now + 1800

        # within 12 hr
        if diff_time < _12hr:
            return now + _1hr

        # within 24 hr
        if diff_time < _24hr:
            return now + _3hr

        # within 48 hr
        if diff_time < _48hr:
            return now + _4hr

        # within 72 hr
        if diff_time < _72hr:
            return now + _6hr

        return now + _24hr







































