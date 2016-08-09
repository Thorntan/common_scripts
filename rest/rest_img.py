#! /usr/bin/env python
#coding=utf-8
"""
    @desc: 抓取并解析tripadvisor餐厅的图片页并解出图片链接，需要提供source_id
"""
from util.Browser import MechanizeCrawler as MC
from common.common import get_proxy,invalid_proxy
import json
import traceback
from lxml import html
import re
import codecs
import db_add
import get_mongo

IMAGE_TABLE = 'tp_rest_img_0707'
BASIC_TABLE = 'tp_rest_basic_0707'

p = get_proxy(source = 'Platform')


def crawl(url):
    global p
    mc = MC()
    #mc.set_debug(True)
    mc.set_proxy(p)
    print 'proxy:',p
    content = mc.req('get', url, html_flag = True,time_out=20)
    count = 0
    while len(content) < 2000:
        invalid_proxy(p,'Platform')
        p = get_proxy(source = 'Platform')
        mc.set_proxy(p)
        print p
        content = mc.req('get', url, html_flag = True,time_out=20)
        count += 1
        if count>5:
            break
    return content

def parse(content,url):
    imgs = []
    sid = re.compile(r'detail=(\d+)').findall(url)[0]
    print 'sid: %s' % sid
    try:
        dom = html.fromstring(content)
    except:
        dom = ''
    flag = 0
    if len(content) < 1000 or len( dom.find_class('noPhotos') ) != 0:
        print 'no photo!!!!!!!!!',sid
        print 'insert',insert_db(('NULL',sid)),sid
        imgs = []
        return 1
    else:
        imgs = dom.find_class('photos inHeroList')[0].xpath('div/@data-bigurl')
        if len(imgs) == 0:
            imgs = dom.find_class('photos inHeroList')[0].xpath('div/@data-bigUrl')
            print 'img 1'
        for i in imgs:
            print 'first pic: %s' % i
            break
        flag = int(len(imgs))

    img_urls = '|'.join(imgs)

    data = (img_urls,sid)
    #data = (sid,url,img_urls,flag)
    print data
    try:
        if len(imgs) !=0:
            print 'insert ',insert_db(data),sid
    except Exception,e:
        print 'insert error',sid,str(e)
    return imgs

def insert_db(args):
    sql = 'update '+BASIC_TABLE+' set image_urls=%s where id=%s'
    return db_add.ExecuteSQL(sql,args)

def get_task():
    sql = 'select * from '+BASIC_TABLE+' where image_urls=\'\' or image_urls is null'
    return db_add.QueryBySQL(sql)

if __name__ in '__main__':
    #url = 'http://www.tripadvisor.cn/LocationPhotoAlbum?detail=719507&geo=187147'
    #parse( crawl(url) )
    count = 0
    for r in get_task():
        print '----- count: %s ----' % count
        url = 'http://www.tripadvisor.cn/LocationPhotoAlbum?detail='+str(r['id']) #+'&geo='+str(r['source_city_id'])
        #url = r.strip()
        print 'url:',url
        try:
            data = parse( crawl(url),url )
        except Exception,e:
            print 'error: %s' % url
            print str(e)
        count += 1
    print count,'over'
    '''
    #task = 'rest_img_page_0128'
    #task = 'tp_rest_page_0707'
    task = 'tp_rest_image_0707013'
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
            print 'url: %s' % url
            if len(content)>500:
                result =  parse( content, url )
        except Exception,e:
            print 'parse error in line %s' % offset
            print str(e)
        offset += 1
    print '%s page over' % str(offset-1)
    '''
