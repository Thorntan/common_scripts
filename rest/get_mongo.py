#! /usr/bin/env python
#coding=utf-8

import sys
import time
from pymongo import MongoClient
import traceback


reload(sys)
sys.setdefaultencoding('utf-8')

_host = '10.10.189.213'
#_host = '10.10.231.105'
_port = 27017
_db = 'platform'


def get_connection():

    client = MongoClient(_host,_port)
    return client

def get_nums(source):

    client = get_connection()
    db = client[_db]

    try:
        collection = db[source]
        count = collection.count()
    except:
        print traceback.print_exc()
    return count


def read_content(source,skip_count,limit_count):

    client = get_connection()
    db = client[_db]
    
    try:
        collection = db[source]
        content = collection.find().skip(skip_count).limit(limit_count)
    except:
        print traceback.print_exc()

    return content[0]

    

if __name__=="__main__":
    
    i = 1
    limit_count = 1
    while i<2:
        print read_content('booking20150808',i,limit_count)
        i+=limit_count
    








