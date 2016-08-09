#! /usr/bin/env python
#coding=utf-8
"""
    @desc: 抓取和解析餐厅评论和翻页评论,需要提供评论页的URL
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
import time

reload(sys)
sys.setdefaultencoding('utf-8')

PROXY = get_proxy(source = 'Platform')
print 'proxy: %s' % PROXY

COMMENT_TABLE = 'tp_rest_comment_0707'
BASIC_TABLE = 'tp_rest_basic_0707'
PAGING_TABLE = 'tp_rest_paging_0707'
LONG_TABLE = 'tp_rest_long_0707'
IS_PAGING_COMMENT = True

def crawl(url):
    global PROXY
    mc = MC()
    mc.set_proxy(PROXY)
    content = mc.req('get', url, html_flag = True)
    count = 0
    while len(content)<1000:
        invalid_proxy(PROXY,'Platform')
        PROXY = get_proxy(source = 'Platform')
        mc.set_proxy(PROXY)
        print 'proxy: %s' % PROXY
        content = mc.req('get', url, html_flag = True)
        count += 1
        if count > 10:
            break
    #open('test.html','w').write(content)
    #content = open('test.html','r').read()
    return content


def parse(content, url, miaoji_id='NULL'):
    content = content.decode('utf-8')
    data_list = []
    root = html.fromstring(content)
    source = 'tripadvisor'
    rest_id = re.compile(r'-d(\d+)').findall(url)[0]

    # 评论详情
    comments = len( root.find_class('reviewSelector') )
    if comments == 0 :
        return data_list
    print '******* reviews *******'
    count = 1
    for rev in root.find_class('reviewSelector')[1:]:
        print '---- %s ---' % count
        review_url = ''
        review_id = ''
        review_title = ''
        review_text = ''
        review_date = ''
        review_grade = ''
        review_user = ''
        user_link = ''
        try:
            is_more_text = len( rev.find_class('partial_entry')[0].find_class('partnerRvw') )
            review_url = 'http://www.tripadvisor.cn' + rev.find_class('quote')[0].xpath('a/@href')[0].strip().encode('utf-8').split('#')[0]
            review_id = re.compile(r'-r(\d+)').findall(review_url)[0]
            review_city_id = re.compile(r'-g(\d+)').findall(review_url)[0]
            review_rest_id = re.compile(r'-d(\d+)').findall(review_url)[0]

            if is_more_text == 0:
                # 短评论
                short_data = short_comment_parse(rev,review_url,miaoji_id,url)
                data_list.append( short_data )
            else:
                # 长评论
                long_comment_url = 'http://www.tripadvisor.cn/ExpandedUserReviews-g%s-d%s?target=%s&context=1&reviews=%s&servlet=Restaurant_Review&expand=1' % (review_city_id,review_rest_id,review_id,review_id)
                print 'long_comment_url:   %s' % long_comment_url
                print 'insert long:',insert_long(long_comment_url.strip())
                #comment_content = crawl(long_comment_url)
                #long_data = long_comment_parse(comment_content,long_comment_url,miaoji_id)
                #data_list.append( long_data )
        except Exception,e:
            print 'comment parse error:'
            print str(e)
        count += 1


    if len(data_list)!=0:
        print 'insert comment',insert_db( data_list ),url
    else:
        print 'no comment',url
    #print '%s comemnts inserted!!!' % len(data_list)
    return data_list

def short_comment_parse(rev,review_url,miaoji_id,url):
    source = 'tripadvisor'
    review_id = re.compile(r'-r(\d+)').findall(review_url)[0]
    review_city_id = re.compile(r'-g(\d+)').findall(review_url)[0]
    review_rest_id = re.compile(r'-d(\d+)').findall(review_url)[0]

    try:
        review_title = rev.find_class('noQuotes')[0].text.strip().encode('utf-8')
    except:
        review_title = ''

    try:
        review_text = rev.find_class('partial_entry')[0].text.strip().encode('utf-8')
    except:
        review_text = ''

    try:
        review_date = '-'.join( re.compile(r'(\d+)').findall( rev.find_class('ratingDate')[0].text.encode('utf-8') ) )
        if len(review_date)<2:
            review_date = rev.find_class('ratingDate')[0].xpath('@title')[0].encode('utf-8')
    except Exception,e:
        review_date = ''

    try:
        grade = '-1'
        review_grade = '-1'
        grade = rev.find_class('rate sprite-rating_s rating_s')[0].xpath('img/@alt')[0].strip().encode('utf-8')
        grade_num = re.compile(r'(\d+)').findall(grade)
        if len(grade_num)>1:
            review_grade = grade_num[0] + '.' + grade_num[1]
        else:
            review_grade = grade_num[0]
    except:
        grade = '-1'
        review_grade = '-1'

    review_user = ''
    try:
        review_user = rev.find_class('expand_inline scrname mbrName_')[0].text.strip().encode('utf-8')
    except:
        review_user = rev.find_class('expand_inline scrname')[0].text.strip().encode('utf-8')

    try:
        user_link = re.compile(r'window.open\(\'(.*)\'\)').findall( rev.find_class('memberBadging')[0].xpath('div/@onclick')[0] )[0].strip().encode('utf-8')
        if user_link.find('http://www.tripadvisor') > -1:
            pass
        else:
            user_link = 'http://www.tripadvisor.cn'+user_link
    except:
        user_link = ''

    print 'review_city_id: %s' % review_city_id
    print 'review_rest_id: %s' % review_rest_id
    print 'review_url: %s' % review_url
    print 'review_id: %s' % review_id
    print 'review_title: %s' % review_title
    print 'review_text:       %s' % review_text
    print 'review_date: %s' % review_date
    print 'review_grade: %s' % review_grade
    print 'review_user: %s' % review_user
    print 'user_link: %s' % user_link
    data = ( source, review_city_id, review_rest_id, review_id, review_title, review_text, review_url, review_date, review_grade, review_user, user_link, url, miaoji_id)
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
    grade = float( '.'.join( re.compile(r'(\d+)').findall( rev.xpath('//*[@class="rate sprite-rating_s rating_s"]/img/@class')[0] )[0] ) )
    user = rev.xpath('//*[@class="username mo"]/span/text()')[0].strip().encode('utf-8')
    user_link = re.compile(r'window.open\(\'(.*)\'\)').findall( rev.xpath('//*[@class="totalReviewBadge badge no_cpu"]/@onclick')[0] )[0].strip().encode('utf-8')
    if user_link.find('http://www.tripadvisor') > -1:
        pass
    else:
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
    return db_add.ExecuteSQLs(sql,args)

def insert_long(args):
    sql = 'insert ignore into '+LONG_TABLE+'(url) values(%s)'
    return db_add.ExecuteSQL(sql,args)

def get_task():
    sql = 'select * from '+PAGING_TABLE;
    return db_add.QueryBySQL(sql)

def delete_paging(args):
    sql = 'delete from '+PAGING_TABLE+' where url = %s'
    return db_add.ExecuteSQL(sql,args)

if __name__ == '__main__':
    #url = 'http://www.tripadvisor.cn/Attraction_Review-g188064-d244427-Reviews-Swiss_Museum_of_Transport-Lucerne.html'
    #try:
    #    parse(crawl(url),url,miaoji_id)
    #except Exception,e:
    #    print str(e)
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
            if IS_PAGING_COMMENT and result:
                print 'delete',delete_paging(url),url
        except Exception,e:
            print 'parse error',str(e)
        count += 1

    print count,'over'
    '''
    task = 'tp_rest_paging_070713'
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
                if IS_PAGING_COMMENT:# and result:
                    print 'delete',delete_paging(url),url
        except Exception,e:
            print 'parse error in page %s' % offset
            print str(e)
        offset += 1
    print '%s page over' % str(offset-1)
    '''
