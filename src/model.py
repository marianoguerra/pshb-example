'''the models to store information'''
import re
import time
import datetime

from google.appengine.ext import db

import val

import gaemodel
from gaemodel import *

class Message(Base):
    # user is the user that originally generated the message
    user        = db.StringProperty(required=True)
    # timeline is the name of the user timeline where this message is stored
    timeline    = db.StringProperty(required=True)
    text        = db.TextProperty(required=True)
    created     = db.DateTimeProperty(auto_now_add=True)
    mentions    = db.StringListProperty(required=True)
    tags        = db.StringListProperty(required=True)

    # list of functions that receive the text and return a list of tags
    TAG_EXTRACTERS = []

    FIELDS = {
        "user": val.fun_str(5),
        "timeline": val.fun_str(5),
        "text": val.fun_str(1),
        "created": val.fun_is_instance(datetime.datetime),
        "mentions": None,
        "tags": None
    }

    OUT_FIELDS = {
        "user": None,
        "timeline": None,
        "text": None,
        "mentions": None,
        "tags": None,
        "created": lambda created: time.mktime(created.timetuple()),
        "key": lambda key: str(key())
    }

    @staticmethod
    def extract_tags(text):
        '''
        return a list of strings with the tags contained in text
        '''

        tags = set()

        for extracter in Message.TAG_EXTRACTERS:
            for tag in extracter(text):
                tags.add(tag)

        return list(tags)

    @staticmethod
    def extract_mentions(text):
        '''
        return a list of strings with the tags contained in text
        '''
        return re.findall("@(\\w+)", text)

def regex_matcher(regex, tags):
    '''
    receive a regex and a list of tags and return a function that receives a text argument and returns
    tags if text matches the regex, if doesn't match, return an empty list
    '''
    compiled = re.compile(regex)

    def matcher(text):
        if compiled.findall(text):
            return tags
        else:
            return []

    return matcher

MATCHERS = (("[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}", ["ip"]),
    ("(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]", ["url"]),
    ("((http|https)://)?www[-A-Za-z0-9]*\\.[-A-Za-z0-9\\.]+(:[0-9]*)?/?", ["link"]),
    ("((http|https)://)?www[-A-Za-z0-9]*\\.[-A-Za-z0-9\\.]+(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]", ["link"]),
    ("(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+(:[0-9]*)?", ["url"]))

for regex, tags in MATCHERS:
    Message.TAG_EXTRACTERS.append(regex_matcher(regex, tags))

def extract_tags(text):
    return re.findall("#(\\w+)", text)

Message.TAG_EXTRACTERS.append(extract_tags)

def set_salt(salt):
    gaemodel.SALT = salt
