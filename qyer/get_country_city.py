# coding=utf-8
'''
	@author:	yanlihua
	@date:	  2015-10-27
	@desc:	  穷游所有国家的城市URL的抓取
	@update:	2015-10-27
'''
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

reload(sys)
sys.setdefaultencoding('utf-8')

def insert_country_data(source, country_id, country_name, country_name_en, country_url):
	sql="insert ignore into qyer_country(source,source_country_id, source_country_name, source_country_name_en, country_url) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (source, country_id, country_name, country_name_en, country_url)
	return db_add.ExecuteSQL(sql)

def insert_city_data(source, country_id, country_name, country_name_en, city_id, city_name ,city_name_en, city_url):
	sql="insert ignore into qyer_city(source,source_country_id, source_country_name, source_country_name_en,source_city_id, source_city_name, source_city_name_en, city_url) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (source, country_id, country_name, country_name_en, city_id, city_name ,city_name_en, city_url)
	db_add.ExecuteSQL(sql)

def get_cities(source,country_id,country_name,country_name_en,country_url):
	page_num = 1
	is_next = 1
	while (is_next == 1):
		#url = "http://place.qyer.com/"+country_name_en.lower()+"/citylist-0-0-" + str(page_num)
		url = country_url+"citylist-0-0-" + str(page_num)
		print url
		mc = MC()
		#mc.set_debug(True)
		page = mc.req('get',url,html_flag=True)
		tree = html.fromstring(page)
		is_next = len(tree.find_class('ui_page_next'))
		num = len(tree.xpath('//*[@class="plcCitylist"]/li'))
		for i in range(1,num+1):
			city_name = tree.xpath('//*[@class="plcCitylist"]/li[%s]/h3/a/text()' % i)[0].strip().encode('utf-8')
			city_name_en = tree.xpath('//*[@class="plcCitylist"]/li[%s]/h3/a/span/text()' % i)[0].strip().encode('utf-8')
			city_url =  tree.xpath('//*[@class="plcCitylist"]/li[%s]/h3/a/@href' % i)[0].strip().encode('utf-8')
			city_id =  tree.xpath('//*[@class="plcCitylist"]/li[%s]/p[5]/@data-pid' % i)[0].strip().encode('utf-8')
			print city_id,city_name,city_name_en,city_url
			insert_city_data(source,country_id,country_name.replace("'","''").encode('utf-8'),country_name_en.replace("'","''"),city_id,city_name.replace("'","''").encode('utf-8'),city_name_en.replace("'","''"),city_url)
		page_num += 1

def qyer_crawl():
	source = 'qyer'
	url = "http://place.qyer.com/"
	# sight/链接没能传进去
	#url = "http://place.qyer.com/"+taskcontent+"/alltravle/"
	mc = MC()
	#mc.set_debug(True)

	# 得到首页
	index_page = mc.req('get',url,html_flag=True)
	tree = etree.HTML(index_page)

	# 国家列表
	country_list = tree.xpath('//*[@class="item"]/a')
	for c in country_list:
		country_id = re.compile(r'(\d+)').findall(c.xpath('@data-bn-ipg')[0])[0]
		country_name = c.xpath('text()')[0].strip().encode('utf-8')
		country_name_en = c.xpath('span/text()')[0].strip().encode('utf-8')
		country_url = c.xpath('@href')[0]
		print '-------------------------------------------------------'
		print country_id,country_name.encode('utf-8'),country_name_en,country_url
		insert_country_data(source,country_id,country_name.replace("'","''"),country_name_en.replace("'","''"),country_url)
		try:
			get_cities(source,country_id,country_name,country_name_en,country_url)
		except Exception,e:
			print str(e)
			continue

	# 热门国家列表
	country_list2 = tree.xpath('//*[@class="item"]/p/a')
	for c in country_list2:
		country_id = re.compile(r'(\d+)').findall(c.xpath('@data-bn-ipg')[0])[0]
		country_name = c.xpath('text()')[0].strip().encode('utf-8')
		country_name_en = c.xpath('span/text()')[0].strip().encode('utf-8')
		country_url = c.xpath('@href')[0]
		print '-------------------------------------------------------'
		print country_id,country_name.encode('utf-8'),country_name_en,country_url
		insert_country_data(source,country_id,country_name.replace("'","''"),country_name_en.replace("'","''"),country_url)
		try:
			get_cities(source,country_id,country_name,country_name_en,country_url)
		except Exception,e:
			print str(e)
			continue


if __name__ in '__main__':
	qyer_crawl()
	#source = 'qyer'
	#country_id = '804'
	#country_name = '梵蒂冈'.encode('utf-8')
	#country_name_en = 'Vatican'
	#country_url = 'http://place.qyer.com/vatican/'
	#get_cities(source,country_id,country_name,country_name_en,country_url)
