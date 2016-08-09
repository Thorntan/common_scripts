#!/usr/bin/env python
#coding=utf-8
'''
    @author:    yanlihua
    @date:      2015-10-27
    @desc:      穷游国内外所有景点的抓取和解析
    @update:    2015-10-28
'''
import sys
from lxml import html as HTML
from util.Browser2 import MechanizeCrawler as MC
import traceback
import re
import time
import db_add
import get_mongo

reload(sys)
sys.setdefaultencoding('utf-8')

def crawl(url):

    ''' 
    根据任务获取所需网页
    '''
    flag = 1 
    mc = MC()
    #mc.set_debug(True)
    for i in range(3):
        page = mc.req('get',url,html_flag = True)
        if page[0]>1500:
            break
    _content = page[0]
    _error = page[1]
    fout = open('test.html','w')
    fout.write(_content)
    fout.close()
    return _content

def parse(content):
    root = HTML.fromstring(content.decode('utf-8'))
    print len(root.find_class('zw-module-bigcard-wrap'))
    offset = 0
    for row in root.find_class('zw-module-bigcard-wrap'):
        print '------ offset: %s ------' % offset
        trip_url = row.xpath('//div/h2/a/@href')[offset]
        title = row.xpath('//div/h2/a/text()')[offset].encode('utf-8').strip()
        num_str = row.find_class('zw-module-bigcard-infonum')[0].text_content().encode('utf-8')
        num = re.compile(r'(\d+)').findall(num_str)
        pv = num[0]
        sales = num[1]
        price_str = row.find_class('zw-module-bigcard-price')[0].text_content().encode('utf-8')
        prices = re.compile(r'(\d+)').findall(price_str)
        original_price = prices[0]
        low_price = prices[1]
        date = row.find_class('zw-module-bigcard-datebar')[0].text_content().encode('utf-8').replace('旅行时间：','').strip().replace(' ','').replace('\t','').rstrip()
        #date = re.sub(" ", " ", date)
        if date.find('永久有效')>-1:
            date = '永久有效'
        else:
            date1 = re.compile(r'(\d+)').findall(date.split('-')[0])
            date2 = re.compile(r'(\d+)').findall(date.split('-')[1])
            date = date1[0]+'/'+date1[1] + '-' + date2[0]+'/'+date2[1]

        
        trip_type =  row.find_class('zw-module-bigcard-infotype')[0].text_content().encode('utf-8').strip()
        place = row.find_class('zw-module-bigcard-infoplace')[0].text_content().encode('utf-8').strip()
        info = row.find_class('zw-module-bigcard-infolist')[0].text_content().encode('utf-8').strip().split('\n')

        print trip_url
        print trip_type
        print place
        print title
        print pv
        print sales
        print original_price 
        print low_price
        print date
        desc_list = []
        for i in info:
            print i.encode('utf-8').strip()
            desc_list.append(i.encode('utf-8').strip())
        desc = str(desc_list)
        data = (trip_url,trip_type,place,title,pv,sales,original_price,low_price,date,desc)
        print 'insert',insert(data)
        offset += 1
    

def insert(args):
    sql = "insert into qyer_freetour(url,type,place,title,pv,sales,original_price,low_price,date,description) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    return db_add.ExecuteSQL(sql,args)

def get_task():
    sql = 'select * from '+TASK_TABLE
    return db_add.QueryBySQL(sql)

if __name__ == '__main__':
    
    #url = 'http://z.qyer.com/flights/all_0_0_0_0_0_0_0/?_channel=freetour&_type=channel'
    for i in range(1,201,1):
        url = 'http://z.qyer.com/all_0_0_0_0_0_0_0/page%s/?_channel=freetour&_type=channel' % i
        try:
            parse(crawl(url))
        except:
            pass
    '''
    sql = 'select date from qyer_freetour'
    r = db_add.QueryBySQL(sql)
    for i in r:
        print i['date'].encode('utf-8').strip()
        break
    '''
