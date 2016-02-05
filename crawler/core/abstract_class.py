# -*- coding: utf-8 -*-
from sqlalchemy import Unicode
from sqlalchemy import Column, Integer, String, DateTime, Float, Index, TIMESTAMP
# from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.engine import reflection
# from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.expression import *
from sqlalchemy import *
from sqlalchemy.orm import *
#from sqlalchemy.dialects.mysql import MEDIUMTEXT, TINYINT
import datetime

Base = declarative_base()

class Stats(Base):
    __tablename__ = 'stats'
    __table_args__ = (Index('my_index', "link", mysql_using='hash'), {'mysql_engine': 'InnoDB',
                     'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'},
                      )
    id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    timestamp = Column(Integer)
    likeCount = Column(Integer, nullable=True, default=0)
    dislikeCount = Column(Integer, nullable=True, default=0)
    shareCount = Column(Integer, nullable=True, default=0)
    commentCount = Column(Integer, nullable=True, default=0)
    viewCount = Column(Integer, nullable=True, default=0)
    fansCount = Column(Integer, nullable=True, default=0)
    rank = Column(Float, nullable=True, default=0)
    link = Column(String(180, collation='utf8_unicode_ci'),
                  nullable=False, index=True)
    board_id = Column(String(150, collation='utf8_unicode_ci'), nullable=True,
                      index=True)
    Index('test_idx2', link, mysql_using='hash')

class Boards(Base):
    # this is another table
    __tablename__ = 'boards'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8',
                      'mysql_collate': 'utf8_general_ci'}
    # this primary key is the foreign key in post.source
    id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    source = Column(String(80, collation='utf8_unicode_ci'))
    board = Column(String(150, collation='utf8_unicode_ci'))
    board_id = Column(String(150, collation='utf8_unicode_ci'),
                      index=True)
    link = Column(String(180, collation='utf8_unicode_ci'), unique=True,
                  index=True)
    fansCount = Column(Integer, nullable=True, default=0)
    enable = Column(Integer)
    rank = Column(Integer, nullable=True, default=0)
    last_check_time = Column(TIMESTAMP, nullable=True, index=True)

class Links(Base):
    # this is another table
    __tablename__ = 'links'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8',
                      'mysql_collate': 'utf8_general_ci'}
    # this primary key is the foreign key in post.source
    id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    link = Column(String(180, collation='utf8_unicode_ci'), unique=True)
    source = Column(String(80, collation='utf8_unicode_ci'), index=True)
    board_id = Column(String(150, collation='utf8_unicode_ci'), index=True)
    title = Column(String(180, collation='utf8_unicode_ci'), nullable=True)
    # last_update_time = Column(DateTime,  nullable=False)
    timestamp = Column(Integer)
    next_update_time = Column(Integer)
    enable = Column(Integer)

class Posts(Base):
    # create a table named posts
    __tablename__ = 'posts'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8',
                      'mysql_collate': 'utf8_general_ci'}
    # define Columns in the new table
    id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    # remove Foreign Key at first
    # source = Column(Integer, ForeignKey('post_link.id'), nullable=False)
    author = Column(String(150, collation='utf8_unicode_ci'))
    board_id = Column(String(150, collation='utf8_unicode_ci'))
    source = Column(String(50, collation='utf8_unicode_ci'))
    board = Column(Unicode(150, collation='utf8_unicode_ci'))
    title = Column(Unicode(768, collation='utf8_unicode_ci'))
    link = Column(String(180, collation='utf8_unicode_ci'), unique=True)
    description = Column(Unicode(768, collation='utf8_unicode_ci'))
    thumbnail = Column(String(150, collation='utf8_unicode_ci'))
    #content = Column(MEDIUMTEXT(collation='utf8_unicode_ci'))
    content = Column(Unicode(768, collation='utf8_unicode_ci'))
    create_time = Column(DateTime)
    timestamp = Column(Integer)
    likeCount = Column(Integer)
    shareCount = Column(Integer)
    commentCount = Column(Integer)
    dislikeCount = Column(Integer)
    viewCount = Column(Integer)
    rank = Column(Float, nullable=True, default=0)
    location = Column(String(50, collation='utf8_unicode_ci'))
    post_type = Column(String(20, collation='utf8_unicode_ci'))
    last_modified = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
    """
    def __init__(self, author, board_id, board, title, link, \
                 description, thumbnail, content, create_time, likeCount, \
                 shareCount, commentCount, dislikeCount, viewCount, location):
        # self.id = id
        # remove source at first
        # self.source = source
        self.author = author
        self.board_id = board_id
        self.board = board
        self.title = title
        self.link = link
        self.description = description
        self.thumbnail = thumbnail
        self.content = content
        self.create_time = create_time
        self.likeCount = likeCount
        self.shareCount = shareCount
        self.commentCount = commentCount
        self.dislikeCount = dislikeCount
        self.viewCount = viewCount
        self.location = location

    def __repr__(self):
        return "Posts('%s', '%i', %s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
               % (self.author, self.board_id, self.board, \
                  self.title, self.link, self.description, self.thumbnail, \
                  self.content, self.create_time, self.likeCount, \
                  self.shareCount, self.commentCount, self.dislikeCount, \
                  self.viewCount, self.location)
    """

class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    title = Column(String(80, collation='utf8_unicode_ci'), unique=True)
    enable = Column(Integer, nullable=True, default=1)
    #import datetime
    #create_date = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    password = Column(String(100))
    email = Column(String(100))
    admin = Column(Integer, nullable=False, default=0)
    activated = Column(Integer, nullable=False, default=0)
    name_sha = Column(String(100, collation='ascii_bin'), nullable=True, default=null)

class Board_Tags(Base):
    __tablename__ = 'table_tags'
    id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    board_id = Column(String(80, collation='utf8_unicode_ci'), nullable=False, index=True)
    tag_id = Column(Integer, nullable=False, index=True)
