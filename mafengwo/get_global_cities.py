# coding=utf-8
'''
    @author:    yanlihua
    @date:      2015-10-16
    @desc:      马蜂窝国外景点URL的抓取
    @update:    2015-10-16
'''
import sys
from util.Browser import MechanizeCrawler as MC
import re
from lxml import etree
import codecs
import db_add
import urllib
import json
import math

reload(sys)
sys.setdefaultencoding('utf-8')

# 得到全球的国家id >>  城市id >> 景点id

def insert(args):
    sql = 'insert ignore into mafengwo_country values(%s,%s,%s,%s,%s)'
    return db_add.ExecuteSQL(sql,args)

def crawl(url):
    '''
    mc = MC()
    #mc.set_debug(True)
    page = mc.req('get',url,html_flag=True)
    open('test.html','w').write(page)
    '''
    content = open('test.html','r').read()
    return content

def get_sight():
    source = 'mafengwo_crawl'
    url = 'http://www.mafengwo.cn/mdd/'
    # 从首页中得到所有country的id
    page = crawl(url)
    tree = etree.HTML(page)
    lines = tree.xpath('//div[@class="row-list"]/div[@class="bd"]/dl')
    print len(lines)
    count = 0
    for con in lines:
        continent = con.xpath('./dt/text()')[0].encode('utf-8')
        print continent
        for c in con.xpath('./dd/ul'):
            #print c
            for li in c.xpath('./li'):
                if len( li.xpath('@class') ) <1:
                    country_url = 'http://www.mafengwo.cn' + li.xpath('./a/@href')[0]
                    country_id = re.compile(r'mafengwo/(\d+)').findall(country_url)[0]
                    country_name = li.xpath('./a/text()')[0].encode('utf-8').strip()
                    country_name_en = li.xpath('./a/span/text()')[0].encode('utf-8').strip()
                    #print country_name_en
                    #print country_id,country_name,country_url
                    data = (country_id,country_name,country_name_en,continent,country_url)
                    print 'insert',insert(data)
                    count += 1
    print 'all:',count
    
    
if __name__ in '__main__':
    get_sight()
    print "all over"
