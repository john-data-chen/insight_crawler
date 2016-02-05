import sys
sys.path.append("../crawler")
import settings
from core.abstract_db import *

class Viral_Ranker(object):

    def __init__(self):
        self.get_rank = eval("self." + settings.RANK_METHOD.lower())
        self.db = sqlalchemy_()
    def get_rank(self):
        return self.get_rank

    def buzzfeed_rank(self, stats):
        _stats = stats.copy()
        rank_weight = {"3":2, "2":1.5, "1":1.2 , "0":1, "-1":0.8, "-2":0.25, "-3": 0.1}
        for k, v in _stats.items():
            if v == -1:
                _stats[k] = 0
        numerator = _stats['likeCount'] + _stats['dislikeCount'] +  \
                    _stats['commentCount'] + _stats['viewCount'] +  \
                    8*_stats['shareCount']

        denominator = _stats['fansCount']
        rank = self.db.get_board_rank(_stats["board_id"])
        return round(numerator / float(denominator), 5) * rank_weight[str(rank)]

    def other_rank(self, stats):
        pass
