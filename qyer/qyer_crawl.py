#coding=utf8
"""
    @desc: 用于抓取穷游各个城市的景点购物美食链接
"""
import sys
from util.Browser import MechanizeCrawler as MC
import re
from lxml import etree
import codecs
import db_add
import urllib
import json
import math
import httplib
from common.common import get_proxy

reload(sys)
sys.setdefaultencoding('utf-8')


# 32,78,147
def get_post_data(page_num,city_type,pid,sort_num):
    data = {
        'page': page_num,
        'type': city_type,
        'pid': pid,
        'sort': sort_num,
        'subsort': 'all',
        'isnominate': -1,
        'haslastm': 'false',
        'rank': 6
        }
    return data
    #return urllib.urlencode(data)

def qyer_crawl(task):
    source = 'qyer'
    city_id = task['source_city_id']
    country_id = task['source_country_id']
    city_name = task['source_city_name'].encode('utf-8')
    city_name_en = task['source_city_name_en'].encode('utf-8')
    country_name = task['source_country_name'].encode('utf-8')
    city_url = task['city_url'].encode('utf-8')
    print "city_url:%s" % city_url

    url = city_url+"alltravel/"

    mc = MC()
    # 得到搜索列表首页
    page = mc.req('get',url,html_flag=True)
    tree = etree.HTML(page)
    # 全部总数
    max_counts = re.compile(r'(\d+)').findall(tree.xpath('//*[@id="poiSort"]/a[1]/text()')[0].encode('utf-8'))[0]
    # 最大页数
    total_counts = int(math.ceil(float(max_counts)/15))
    print "全部%s个(景点美食购物活动),共有%s页: " % (max_counts, total_counts)
    total_attr = re.compile(r'(\d+)').findall(tree.xpath('//*[@id="poiSort"]/a[2]/text()')[0].encode('utf-8'))[0]
    total_rest = re.compile(r'(\d+)').findall(tree.xpath('//*[@id="poiSort"]/a[3]/text()')[0].encode('utf-8'))[0]
    total_shop = re.compile(r'(\d+)').findall(tree.xpath('//*[@id="poiSort"]/a[4]/text()')[0].encode('utf-8'))[0]
    print total_attr,total_rest,total_shop

    if (max_counts != 0):
        # 翻页post数据
        script_content = tree.xpath('/html/head/script[1]/text()')[0]
        pid = re.compile(r'PID :\'(\d+)\'').findall(script_content)[0].strip().encode('utf-8')
        city_type = re.compile(r'TYPE:\'(.+)\'').findall(script_content)[0].strip().encode('utf-8')
        paging(city_id, total_attr, city_type, pid, 32)
        paging(city_id, total_rest, city_type, pid, 78)
        paging(city_id, total_shop, city_type, pid, 147)
    print "%s complete!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" % city_id


def paging(city_id, total_counts,  city_type, pid, sort_num):
    mc = MC()
    max_page = int(math.ceil(float(total_counts)/15))
    print max_page
    old_id_list = []
    url_paging = "http://place.qyer.com/poi.php?action=list_json"
    for page_num in range(1,max_page+1 ):
        print "第%s页" % page_num
        json_data = mc.req('post', url_paging, get_post_data(page_num, city_type, pid, sort_num), paras_type = 0, html_flag=True)
        data = json.loads(json_data)
        try:
            id_list = get_detail(data,city_id)
        except:
            id_list = []
        if len( list(set(id_list).difference(set(old_id_list))) ) == 0 :
            print id_list
            print old_id_list
            print "duplicate"
            break
        old_id_list = id_list

def get_detail(data,city_id):
    source = 'qyer'
    id_list = []
    info_list = []
    for i in data['data']['list']:
        try:
            catename = i['catename'].encode('utf-8')
        except:
            catename = 'NULL'
        sight_id = i['id'].encode('utf-8')
        sight_url = i['url'].encode('utf-8')
        cnname = i['cnname'].encode('utf-8')
        enname = i['enname'].encode('utf-8')
        rank = i['rank']
        grade = i['grade']
        comments = str(i['commentCount'])
        print catename.encode('utf-8'),sight_id,sight_url
        # 插入数据库
        #info = (sight_id, source, city_id, city_name, city_name_en, country_id, country_name, sight_url,catename)
        #info = (sight_id, source, city_id, sight_url, catename)
        info = (sight_id, source, city_id, sight_url, catename, cnname, enname, rank, grade, comments)
        info_list.append(info)
        id_list.append(sight_id)
    print "got url:",len(info_list)
    print 'insert',insert_db( info_list )
    return id_list


def get_city(args):
    sql = 'select * from qyer_city where source_country_id = %s and source_city_name = %s'
    return db_add.QueryBySQL(sql,args)

def insert_db(args):
    #sql = 'insert ignore into qyer_spain(id,source,source_city_id,source_city_name,source_city_name_en,source_country_id,source_country_name,url,cateid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    #sql = 'insert ignore into qyer_spain(id,source,city_id,url,cateid) values(%s,%s,%s,%s,%s)'
    sql = 'insert ignore into qyer(id,source,source_city_id,url,cateid, name, name_en, ranking, grade, commentcounts) values(%s,%s,%s,%s,%s, %s,%s,%s,%s,%s)'
    return db_add.ExecuteSQLs(sql,args)

def get_task():
    #sql = "select city_url, source_city_id,source_city_name,source_city_name_en,source_country_id,source_country_name from qyer_city where source_city_id = \'6640\' " #in (6655,6653)"
    #sql = "select city_url, source_city_id,source_city_name,source_city_name_en,source_country_id,source_country_name from qyer_city where source_city_id in('8858','8804','9820','9818','7454','9815','9954','9933') " #in (6655,6653)"
    #sql = "select city_url, source_city_id,source_city_name,source_city_name_en,source_country_id,source_country_name from qyer_city where date > '2016-03-21'"
    #sql = "select *  from tp_city where qyer_url is not null"
    #sql = "select * from qyer_city where  source_city_id='9891' order by source_city_id"
    sql = "select * from qyer_city where  total is not null and total!=0 order by source_city_id"
    results = db_add.QueryBySQL(sql)
    return results

if __name__ in '__main__':
    print 'all',len(get_task())
    count = 1
    for task in get_task():
        #print '-'*5,count,'-'*5
        try:
            qyer_crawl(task)
        except Exception,e:
            print 'error: %s' % task
            print str(e)
        count += 1
