#!/usr/bin/env python
# coding=utf-8
'''
    @author:    yanlihua
    @date:      2015-10-26
    @desc:      百度旅游国内外所有景点页面的抓取和解析
    @update:    2015-10-28
'''
import sys
import urllib
from util.Browser2 import MechanizeCrawler as MC 
from lxml import html
import random
import re
import traceback
import db_add
#from logger import logger

reload(sys)
sys.setdefaultencoding('utf-8')

comment_pat = re.compile(r'(\d+)',re.S)
CONTENT_LEN = 100


class BaiduParser():

    def __init__(self):
        pass

    def crawl(self,url,flag = False):
    
        crawl_flag = self.baidu_crawl(url)
        return crawl_flag 


    def baidu_crawl(self,url):

        ''' 
        根据任务获取所需网页
        '''
        info = {}
        flag = 1 
        url = url
        mc = MC()
        #mc.set_debug(True)
        for i in range(3):
            page = mc.req('get',url,html_flag = True)
            if page[0]>CONTENT_LEN:
                break
        _content = page[0]
        _error = page[1]
        '''
        fout = open('baidu.html','w')
        fout.write(_content)
        fout.close()
        '''
        try:
            info = page_parser(_content,url)
            #logger.info('Parser Finish [%s] [%s] [%s] [%s] [%s] [%s]'%(info))
            return 0,info
        except:
            #print traceback.print_exc()
            pass
            #logger.info('Parser Failed')
            return 1,info



def page_parser(content,url):
    content = content.decode('utf-8')
    root = html.fromstring(content)
    
    source = 'baidu'
    try:
        source_id = re.compile(r'data-sid="(.*)" data-newDirective').findall(content)[0].strip().encode('utf-8')
    except:
        source_id = 'NULL'
    #print 'source_id'
    #print source_id

    try:
        name_py = root.find_class('main-name')[0].xpath('a/@href')[0].replace('/','').strip().encode('utf-8').replace("'","''")
    except:
        name_py = 'NULL'
    #print 'name_py'
    #print name_py

    try:
        name = root.find_class('main-name')[0].xpath('a/text()')[0].strip().encode('utf-8').replace("'","''")
    except:
        name = 'NULL'
    #print 'name'
    #print name

    try:
        name_en = root.xpath('//*[@class="deputy-name"]/a/text()')[0].encode('utf-8').strip().replace("'","''")
    except:
        name_en = 'NULL'

    #print 'name_en'
    #print name_en

    grade = 'NULL'
    try:
        '''
        star_pat = re.compile(r'(\d+)')
        t_star = root.xpath('//div[@class="main-score"]/text()')[1].encode('utf-8').strip()
        grade = t_star[:-3] 
        if '.' in grade:
            star = int(float(t_star[:-3]) +0.5)
        else:
            star = int(t_star[:-3])
        '''
        star_num = re.compile(r'(\d+)').findall(root.xpath('//*[@class="star-new"]/span/@class')[0])[0]
        if star_num == '0':
            star = 0
            grade = 0
        else:
            star = int(star_num)/2.0
            grade = star
    except Exception,e:
        #print str(e)
        star = -1
    #print 'star'
    #print star
    #print 'grade'
    #print grade

    try:
        commnum = root.xpath('//*[@class="main-score"]/a/text()')[0].encode('utf-8').strip()
        commentcounts = int(re.compile(r'(\d+)').findall(commnum)[0])
    except Exception, e:
        #print str(e)
        commentcounts = 'NULL'
    #print 'commentcounts'
    #print commentcounts
    
    try:
        rank = root.xpath('//span[@class="point-rank"]/span/text()')[0]
        rank = int(rank.encode('utf-8').strip())
    except:
        rank = 'NULL' 
    #print 'rank'
    #print rank
    
    try:
        img_url = root.xpath('//span[@class="pic-count"]/a/@href')[0]
        img_url = 'http://lvyou.baidu.com' +img_url.encode('utf-8').strip().replace("'","''")
    except:
        img_url = 'NULL'
    #print 'img_url'
    #print img_url
    
    try:
        desc_pat = re.compile(r'more_desc:\"(.*?)\",')#.encode('utf-8').strip()
        desc = desc_pat.findall(content)[0].decode('unicode-escape').encode('utf-8').replace("'","''")
    except Exception,e:
        #print str(e)
        des = 'NULL'
    #print 'desc'
    #print desc
    
    try:
        map_info = re.compile(r'map_info:\"(.*?)\"').findall(content)[0].encode('utf-8').strip()
    except Exception,e:
        # str(e)
        map_info = 'NULL'
    #print 'map_info'
    #print map_info
    
    try:
        address_pat = re.compile(r'address:\"(.*?)\",')
        address_str = address_pat.findall(content)[0].encode('utf-8').strip()
        # 从页面中得到的address是unicode字符串
        address = address_str.decode('unicode_escape').encode('utf-8').replace("'","''")

        if address == '':
            addr_list = []
            temp_addr_list = root.xpath('//*[@class="dest-crumbs"]/a')
            for i in temp_addr_list[2:]:
                addr_list.append(i.xpath('text()')[0].encode('utf-8').replace("'","''"))
            # 插入逗号作为间隔
            sep = str(',').encode('utf-8')
            address = sep.join(addr_list)
    except Exception,e:
        #print str(e)
        address = 'NULL'
    #print 'address'
    #print address.encode('utf-8')
    
    try:
        phone_pat = re.compile(r'phone:\"(.*)\"')
        phone = phone_pat.findall(content)[0]
        if phone == '':
            phone = 'NULL'
    except Exception,e:
        #print str(e)
        phone = 'NULL'
    #print 'phone'
    #print phone
    
    cateid = 'NULL'
    recommend_time = 'NULL'
    try:
        info_dict = {}
        temp = root.xpath('//div[@class="main-intro"]/span/span/text()')
        for each in temp:
            t = each.encode('utf-8').strip()
            #print t.encode('utf-8')
            if '：' in t:
                info_dict[t.split('：')[0]] = t.split('：')[1]
        cateid = info_dict['景点类型']
        recommend_time = info_dict['建议游玩']
    except Exception,e:
        #print str(e)
        recommend_time = 'NULL'
    #print 'recommend_time'
    #print recommend_time
    #print 'cateid'
    #print cateid

    try:
        site = re.compile(r'website:\"(.*)\"').findall(content)[0]
        if site == '':
            site = 'NULL'
    except Exception,e:
        site = 'NULL'
    #print 'site'
    #print site
    
    md5sum = 'NULL'
    price = 'NULL'
    flag = 0
    tuple = (source,name,name_en,name_py,map_info,address,star,commentcounts,grade,phone,img_url,desc,rank,cateid,recommend_time,site,source_id)
    
    #insert_db(tuple)


def insert_db(args):
    
    ''' 
    插库函数
    '''
    sql = 'update baidu set source =  \'%s\',name =  \'%s\',name_en =  \'%s\',name_py =  \'%s\',map_info =  \'%s\',address =  \'%s\',star =  \'%s\', commentcounts =  \'%s\',grade =  \'%s\', phone =  \'%s\',imgurl =  \'%s\',introduction =  \'%s\',ranking =  \'%s\',cateid =  \'%s\',recommended_time =  \'%s\', site = \'%s\' where id = \'%s\'' % args
#    sql = "update baidu set source =  %s,name =  %s,name_en =  %s,name_py =  %s,map_info =  %s,address =  %s,star =  \'%s\', commentcounts =  \'%s\',grade =  \'%s\', phone =  \'%s\',imgurl =  \'%s\',introduction =  \'%s\',ranking =  \'%s\',cateid =  \'%s\',recommended_time =  \'%s\', site = \'%s\' where id = \'%s\'"
    #print sql.encode('utf-8')
    return db_add.ExecuteSQL(sql)


def get_url():
    sql = 'select url from baidu where map_info is null'
    result = db_add.QueryBySQL(sql)
    return result

            

if __name__ == '__main__':
    ##url = 'http://lvyou.baidu.com/pipidao'
    #url = 'http://lvyou.baidu.com/taiguoqingdao'
    #url = 'http://lvyou.baidu.com/qingdaoshandong'
    #url = 'http://lvyou.baidu.com/gugong'
    a = BaiduParser()
    #a.crawl(url)
    for i in get_url()[:100]:
        url = i['url'].encode('utf-8').replace(" ","%20")
        print '------------------------------------------------'
        print i['url'].encode('utf-8')
        #print url
        try:
            a.crawl(url)
        except Exception,e:
           print 'fail !!!!!!!!!'
            continue
