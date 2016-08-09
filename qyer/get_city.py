# coding=utf-8
'''
    @author:    yanlihua
    @date:      2015-10-27
    @desc:      穷游单个国家城市URL的抓取
    @update:    2015-10-27
'''
import sys
from util.Browser import MechanizeCrawler as MC
import re
from lxml import etree
from lxml import html
import codecs
import db_add

reload(sys)
sys.setdefaultencoding('utf-8')

def insert_db(name,name_en,url):
    sql="replace into city(city_name,city_name_en,city_url) values (\'%s\',\'%s\',\'%s\')" % (name,name_en,url)
    db_add.ExecuteSQL(sql)

def get_cities(country_name_en):
    page_num = 1
    is_next = 1 
    while (is_next == 1):
        url = "http://place.qyer.com/"+country_name_en+"/citylist-0-0-" + str(page_num)
        mc = MC()
        page = mc.req('get',url,html_flag=True)
        content = page.decode('utf-8')
        tree = html.fromstring(content)
        is_next = len(tree.find_class('ui_page_next'))
        num = len(tree.xpath('//*[@class="plcCitylist"]/li'))
        for i in range(1,num+1):
            city_name = tree.xpath('//*[@class="plcCitylist"]/li[%s]/h3/a/text()' % i)[0].strip().encode('utf-8')
            city_name_en = tree.xpath('//*[@class="plcCitylist"]/li[%s]/h3/a/span/text()' % i)[0].strip().encode('utf-8')
            city_url =  tree.xpath('//*[@class="plcCitylist"]/li[%s]/h3/a/@href' % i)[0].strip().encode('utf-8')
            print city_name,city_name_en,city_url
            #insert_db(city_name,city_name_en,city_url)
        page_num += 1

if __name__ in '__main__':
    country = 'australia'
    country = 'fiji'
    country_name_en = 'spain'
    get_cities(country_name_en)
