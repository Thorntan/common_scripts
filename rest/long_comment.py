#! /usr/bin/env python
#coding=utf-8
"""
    @desc: 抓取和解析tripadvisor长评论，需要长评论的URL
"""
import sys
from util.Browser import MechanizeCrawler as MC
from common.common import get_proxy,invalid_proxy
import json
import traceback
from lxml import html
import re
import db_add
import get_mongo
#import rest_comment2
import os
import json

reload(sys)
sys.setdefaultencoding('utf-8')

PROXY = get_proxy(source = 'Platform')
print 'proxy: %s' % PROXY

COMMENT_TABLE = 'tp_rest_comment_051102'
LONG_TABLE = 'tp_rest_long_0511'

def crawl(url):
    global PROXY
    mc = MC()
    #mc.set_debug(True)
    mc.set_proxy(PROXY)
    content = mc.req('get', url, html_flag = True,time_out=15)
    count = 0
    while len(content)<1000:
        invalid_proxy(PROXY,'Platform')
        PROXY = get_proxy(source = 'Platform')
        mc.set_proxy(PROXY)
        print 'proxy: %s' % PROXY
        content = mc.req('get', url, html_flag = True,time_out=15)
        count += 1
        if count > 10:
            break
    return content


def parse(content, url, miaoji_id='NULL'):
    content = content.decode('utf-8')
    data_list = []
    root = html.fromstring(content.decode('utf-8'))
    source = 'tripadvisor'
    rest_id = re.compile(r'-d(\d+)').findall(url)[0]
    #long_comment_url = 'http://www.tripadvisor.cn/ExpandedUserReviews-g%s-d%s?target=%s&context=1&reviews=%s&servlet=Restaurant_Review&expand=1' % (review_city_id,review_rest_id,review_id,review_id)
    #print 'insert long:',insert_long(url)
    data = long_comment_parse(content,url,miaoji_id)
    print 'insert comment',insert_db( data ),url
    return data

def long_comment_parse(content,url,miaoji_id='NULL'):
    rev = html.fromstring(content.decode('utf-8'))
    source = 'tripadvisor'
    review_id = re.compile(r'target=(\d+)').findall(url)[0]
    city_id = re.compile(r'-g(\d+)').findall(url)[0]
    rest_id = re.compile(r'-d(\d+)').findall(url)[0]
    review_url = 'http://www.tripadvisor.cn/ShowUserReviews-g%s-d%s-r%s.html' % (city_id,rest_id,review_id)
    print review_id,city_id

    title = rev.find_class('noQuotes')[0].text.strip().encode('utf-8')
    comment = rev.find_class('entry')[0].xpath('p/text()')[0].strip().encode('utf-8')
    try:
        date = rev.xpath('//*[@class="ratingDate relativeDate"]/@title')[0]
    except Exception,e:
        date_str = rev.xpath('//*[@class="ratingDate"]/text()')[0].strip().encode('utf-8')
        date = '-'.join( re.compile(r'(\d+)').findall( date_str ) )
    try:
        grade = float( '.'.join( re.compile(r'(\d+)').findall( rev.xpath('//*[@class="rate sprite-rating_s rating_s"]/img/@class')[0] )[0] ) )
    except:
        grade = ''
    try:
        user = rev.xpath('//*[@class="username mo"]/span/text()')[0].strip().encode('utf-8')
    except:
        user = ''
    try:
        user_link = re.compile(r'window.open\(\'(.*)\'\)').findall( rev.xpath('//*[@class="totalReviewBadge badge no_cpu"]/@onclick')[0] )[0].strip().encode('utf-8')
    except:
        user_link = ''
    if user_link.find('http://www.tripadvisor') > -1:
        pass
    else:
        if user_link:
            user_link = 'http://www.tripadvisor.cn'+user_link
    print 'city_id: %s' % city_id
    print 'rest_id: %s' % rest_id
    print 'review_url: %s' % review_url
    print 'review_id: %s' % review_id
    print 'title: %s' % title
    print 'comment:       %s' % comment
    print 'date: %s' % date
    print 'grade: %s' % grade
    print 'user: %s' % user
    print 'user_link: %s' % user_link
    data = ( source, city_id, rest_id, review_id, title, comment, review_url, date, grade, user, user_link, url, miaoji_id )
    return data


def insert_db(args):
    sql = 'insert ignore into '+COMMENT_TABLE+'(source, source_city_id, source_id, review_id, review_title, review_text, review_link, comment_time, comment_rating, user_name, user_link, review_from, miaoji_id ) values(%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s)' # on duplicate key update review_from=values(review_from)'
    return db_add.ExecuteSQL(sql,args)

def get_task():
    sql = 'select * from '+LONG_TABLE;
    return db_add.QueryBySQL(sql)

def delete_long(args):
    sql = 'delete from '+LONG_TABLE+' where url = %s'
    return db_add.ExecuteSQL(sql,args)

if __name__ == '__main__':
    #url = 'http://www.tripadvisor.cn/Attraction_Review-g188064-d244427-Reviews-Swiss_Museum_of_Transport-Lucerne.html'
    #try:
    #    parse(crawl(url),url,miaoji_id)
    #except Exception,e:
    #    print str(e)
    '''
    count = 0
    for u in get_task():
        try:
            print '----- count: %s ------' % count
            url = u['url']
            print 'url: %s' % url
            try:
                miaoji_id = u['miaoji_id']
            except:
                miaoji_id = 'NULL'
            result = parse(crawl(url),url,miaoji_id)
            if result:
                print 'delete',delete_long(url),url
        except Exception,e:
            print 'parse error',str(e)
        count += 1
        #break
    print count,'over'
    '''
    task = 'tp_rest_long_051124'
    page_nums = get_mongo.get_nums( task )
    print 'all page:%s' % page_nums
    offset = 1
    limit_count = 1
    while offset <= page_nums:
        print 'offset: %s' % offset
        try:
            page = get_mongo.read_content( task, offset, limit_count )
            content = page['content']
            url = page['url']
            print '--------------------- offset: %s ------------------------' % offset
            print 'url:',url
            if len(content)>1000:
                result =  parse( content, url )
                if result:
                    print 'delete',delete_long(url),url
        except Exception,e:
            print 'parse error in page %s' % offset
            print str(e)
        offset += 1
    print '%s page over' % str(offset-1)

    ##'''
    #data_dir = '/data/yanlihua/tp_rest_paging_051103/'
    #os.chdir(data_dir)
    #for f in os.listdir('./'):
    #    print f
    #    for i in open(f,'r'):
    #        d = json.loads(i)
    #        url = d['url']
    #        content = d['content']
    #        open('/tmp/test.html','w').write(content)
    #        print 'url:',url
    #        '''
    #        if len(content)>1000:
    #            try:
    #                result =  parse( content, url )
    #                #if result:
    #                #    print 'delete',delete_long(url),url
    #            except:
    #                pass
    #        '''
    #        break
    #    break
    #'''
