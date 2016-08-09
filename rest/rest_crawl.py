# coding=utf-8
import sys
from util.Browser import MechanizeCrawler as MC
import re
from lxml import etree
from lxml import html
import codecs
import db_add
import urllib
import json
import math
import httplib
from common.common  import get_proxy,invalid_proxy
import time

reload(sys)
sys.setdefaultencoding('utf-8')

CITY_TABLE = 'tp_city'

p = get_proxy(source='Platform')
#p = ''

def insert_db(args):
    sql = 'insert ignore into tp_rest_basic_0707(source, city_id, id, res_url) values(%s,%s,%s,%s)'
    return db_add.ExecuteSQLs(sql,args)

def crawl(city_url,city_id):
    global p
    source = 'daodao'
    #city_url = city_url.replace('Tourism','Restaurants')
    print city_url
    mc = MC()
    mc.set_proxy(p)
    print 'proxy:  %s' % p
    page1 = ''
    page1 = mc.req('get',city_url,html_flag=True, time_out=10)
    count =0
    while len(page1)<1000:
        invalid_proxy(p,'Platform')
        p = get_proxy(source='Platform')
        print 'proxy: %s' % p
        mc.set_proxy(p)
        page1 = mc.req('get',city_url,html_flag=True , time_out=10)
        count += 1
        if count > 20:
            break
    source_city_id = re.compile(r'-g(\d+)').findall(city_url)[0]
    root = html.fromstring(page1)

    # 城市餐厅总数
    rating_info = root.find_class('listing')[0].find_class('popIndexDefault')[0].xpath('text()')[0].encode('utf-8').strip().split('(')[1].replace(',','')
    nums = re.compile(r'(\d+)').findall(rating_info)
    res_total = int(nums[0])
    print "total: %s " % res_total

    # 第一页的餐厅列表
    items = root.find_class('listing')
    data_list = []
    for item in items:
        res_url = 'http://www.tripadvisor.cn' + item.find_class('title')[0].xpath('a/@href')[0].strip().encode('utf-8')
        res_id = re.compile(r'd(\d+)').findall(res_url)[0].encode('utf-8')
        print res_url
        data = (source,city_id,res_id,res_url)
        print data
        data_list.append(data)
    print 'insert',insert_db(data_list)


    print '------------next page------------'
    itag = '10591' # 餐厅的类别id
    page = 2
    data_list = []
    for offset in range(30,res_total+1,30):
        print '-----------page %s-------' % page
        page += 1
        next_url = 'http://www.tripadvisor.cn/RestaurantSearch?Action=PAGE&geo=%s&ajax=1&itags=%s&sortOrder=popularity&o=a%s&availSearchEnabled=false' % (source_city_id,itag,offset)
        print next_url

        content2 = ''
        content2 = mc.req('get',next_url,html_flag = True)
        while (len(content2) < 1000):
            p = get_proxy(source='Platform')
            print 'proxy: %s' % p
            content2 = mc.req('get',next_url,html_flag = True)
        no_count = len( re.compile(r'(该餐馆暂无点评，来写第一条)').findall(content2) )
        # 如果大部分是“该餐馆暂无点评，来写第一条”，就停止翻页
        if int(no_count) >29:
            break
        root2 = html.fromstring(content2)
        items = root2.find_class('listing')
        data_list2 = []
        for item in items:
            res_url = 'http://www.tripadvisor.cn' + item.find_class('title')[0].xpath('a/@href')[0].strip().encode('utf-8')
            res_id = re.compile(r'd(\d+)').findall(res_url)[0].encode('utf-8')
            print res_url
            data2 = (source,city_id,res_id,res_url)
            print data2
            data_list2.append(data2)
        print 'insert',insert_db(data_list2)
    print 'city %s ok' % city_id

def get_task():
    sql = 'select * from '+CITY_TABLE+" where flag='japan2' order by city_id"
    result = db_add.QueryBySQL(sql)
    return result

if __name__ in '__main__':
    count = 0
    for task in get_task()[1:]:
        city_id = task['city_id']
        url = task['url'].encode('utf-8')
        url = url.replace('Tourism-g','Restaurants-g')
        count += 1
        try:
            print '----------city_count: %s ------' % count
            print "city: %s" % url
            crawl(url,city_id)
        except Exception,e:
            print 'error: %s' % url
            print str(e)
        if not p:
            time.sleep(2)
    print count,'over'
