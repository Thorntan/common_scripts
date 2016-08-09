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
    
    
    # ------------- 使用示例 ------------
    # 平台抓取的任务
    task = 'ctrip_052402'
    # 抓取任务的总数
    total = get_mongo.get_nums( task )
    print 'all page:%s' % total

    offset = 1  # 从第一条数据开始读
    limit_count = 1 # 每次读取一条数据
    while offset <= total:
        print 'offset: %s' % offset
        try:
            data = get_mongo.read_content( task, offset, limit_count )
            # 读取的每条数据都是一个dict：url是抓取页面的链接，content是抓取下来的页面内容
            url = data['url']
            content = data['content']
            #open('test.html','w').write(content)
            print '---- offset: %s -----' % offset
            #  如果页面大小大于1000，则进行解析. 否则判断为不完整的页面，跳过。
            if len(content)>1000:
                # ------------ 解析页面的方法  ------------
                your_parser( content, url )
        except Exception,e:
            print 'parse error in page %s' % offset
            print str(e)
        offset += 1
    print '%s rest over' % str(offset-1)








