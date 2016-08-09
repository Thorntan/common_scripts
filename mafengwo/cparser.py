#!/usr/bin/env python
# coding=utf-8
'''
    @author:    yanlihua
    @date:      2015-10-16
    @desc:      马蜂窝所有景点页面的抓取和解析
    @update:    2015-10-16
'''
import get_mongo
import lxml.html as HTML
import re
import traceback
from util.Browser2 import MechanizeCrawler as MC 
#from util.Browser import MechanizeCrawler as MC 
import time
import sys
from common.logger import logger
import db_add
import json
from common.common  import get_proxy
import codecs

reload(sys)
sys.setdefaultencoding('utf-8')


map_pat = re.compile('"lat":(.*?),"lng":(.*?),', re.S|re.M)

id_pat = re.compile(r'poi/(.*?).html', re.S)

name_pat = re.compile(r'(\(.*\))',re.S)

comments_pat = re.compile(r'(\d+)',re.S)
rank_pat = re.compile(r'(\d+)',re.S)

def has_chinese(contents,encoding='utf-8'):
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    if not isinstance(contents,unicode):
        u_contents = unicode(contents,encoding=encoding)
    results = zh_pattern.findall(u_contents)
    #for i in range(len(results)):
    #    print 'has chinese',results[i].encode(encoding)
    if len(results) > 0:
        return True
    else:
        return False


class MafengwoParser():
    def __init__(self):
        pass

    def crawl(self,url):

        crawl_flag = 1
        crawl_flag = self.mafengwo_crawl(url)
        return crawl_flag

    def mafengwo_crawl(self,url):
        
        info = {}
        mc = MC()
        #p = get_proxy(source='Platform')
        p = '1.173.108.243:8088'
        #mc.set_proxy(p)
        page = mc.req('get',url,html_flag = True)
        _content = page[0]
        _err = page[1]
        '''
        fout = open('mafengwo.html','w')
        fout.write(_content)
        fout.close()
        '''
        #_content = open('mafengwo.html','r').read()
        
        try:
            info = parse(_content,url)
            #logger.info('Parser Finish [%s] [%s] [%s] [%s] [%s] [%s]'%(info))
            return 0,info
        except:
            print traceback.print_exc()
            #logger.info('Parser Failed')
            return 1,info


def parse(content,url):
    
    dict = {}
    attr_list = []
    alias = ''
    name_en = ''
    nearby_id = ''
    source_id = ''
    address = ''

    source_id = url.split('/')[4].replace('.html','')
    print 'sid:',source_id

    root = HTML.fromstring(content.decode('utf-8'))

    try:
        name_zh = root.xpath('//div[@class="s-title"]/h1/text()')[0]
        name_zh = name_zh.strip().encode('utf-8')
    except:
        try:
            name_zh = root.xpath('//div [@class="title clearfix"]/div[1]/h1/text()')[0]
            name_zh = name_zh.encode('utf-8').strip()
        except Exception,e:
            name_zh = ''
    print 'name_zh:',name_zh
    name = name_zh
    
    try:
        t_name_en = root.xpath('//div [@class="s-title"]/p/span/text()')[0]
        name_en = t_name_en.strip().encode('utf-8').replace('（','').replace('）','').replace("'","''")
    except:
        try:
            t_name_en = root.xpath('//div [@class="title clearfix"]/text()')[0]
            t_name_en = t_name_en.encode('utf-8').strip().replace("'","''")
        except Exception,e:
            print str(e)
            name_en = ''
    
    if has_chinese(name_en):
        name_en = ''

    print 'name_en:',name_en

    try:
        img_url = root.xpath('//a [@class="photo"]/@href')[0].encode('utf-8').strip()
        img_url = 'http://www.mafengwo.cn' + img_url
    except:
        try:
            img_url = root.xpath('//div[@class="pic-r"]/a/@href')[0].encode('utf-8').strip()
            img_url = 'http://www.mafengwo.cn' + img_url
        except Exception,e:
            print str(e)
            img_url = ''
    
    print 'img_url'
    print img_url
    
    try:
        t_ranking = root.xpath('//div [@class="ranking"]/em/text()')[0]
        ranking = rank_pat.findall(t_ranking)[0]
    except:
        ranking = '2000000'

    print 'ranking'
    print ranking
    try:
        grade = root.find_class('txt-l')[0].xpath('div[1]/span/em/text()')[0].strip()
    except Exception, e:
        grade = '-1'
    
    print 'grade'
    print grade
    try:
        star = root.find_class('txt-l')[0].xpath('div[1]/span[2]/div[1]/span/@class')[0]
        star = star.replace('star','')
    except:
        star = -1
    print 'star'
    print star
    
    try:
        address = root.xpath('//div [@class="r-title"]/div/text()')[0]
        address = address.strip().encode('utf-8')
    except:
        try:
            address = root.xpath('//div[@class="col-side _j_rside"]/div[3]/ul/li[1]/text()')[0]
            address = address.encode('utf-8').strip().replace("'","''")
        except Exception,e:
            print str(e)
            address = ''
    print 'address'
    print address
    try:
        comment_num = root.xpath('//div[@class="row row-reviews"]/div/div/p/em/text()')[0]
        comment_num = comment_num.encode('utf-8').strip()
    except:
        try:
            t_comment = root.xpath('//div [@class="m-box m-content"]/div/span/text()')[0].\
                    encode('utf-8').strip()
            comment_num = comments_pat.findall(t_comment)[0]
        except Exception,e:
            print str(e)
            comment_num = -1
    
    print 'comment_num'
    print comment_num

    try:
        beencounts = root.xpath('//a[@class="btn-been"]')[0].xpath('descendant::*[@class="pa-num"]/text()')[0].encode('utf-8')
    except:
        beencounts = -1
    print 'beencounts'
    print beencounts
    try:
        desc = root.xpath('//div [@class="row row-overview"]/div[4]/dl/dt/p/span')[0].xpath('string(.)')
        desc = desc.encode('utf-8').strip().replace("'","''")
    except Exception,e:
        print str(e)
        desc = ''
    print 'desc'
    print desc
    phone = ''
    site = ''
    wayto = ''
    price = ''
    opentime = ''
    re_time = ''
    alias = ''
    for row in root.xpath('//span[@class="label"]'):
        label = row.xpath('text()')[0].encode('utf-8').strip()
        text = row.xpath('following-sibling::p')[0].xpath('string(.)').encode('utf-8')
        if label =='门票':
            text = text.replace('\n','').strip()
            price = text
        elif label == '交通':
            wayto  = text
        elif label == '电话':
            phone = text
        elif label == '开放时间':
            opentime = text
        elif label == '用时参考':
            re_time = text
        elif label == '当地名称':
            alias = text
        elif label == '网址':
            site = text
        else:
            pass
    

    print 'wayto'
    print wayto
    print 'price'
    print price
    print 'opentime'
    print opentime
    print 're_time'
    print re_time
    print 'site'
    print site
    print 'alias',alias
    try:
        map_info_temp = map_pat.findall(content)[0]
        map_info = map_info_temp[1] + ',' + map_info_temp[0]
    except Exception, e:
        map_info = ''
    print 'map_info'
    print map_info
    
    source = 'mafengwo'
    
    #tuple = (source,name,name_en,map_info,address,star,comment_num,grade,phone,site,\
    tuple = (source,address,star,comment_num,grade,phone,site,\
            img_url,desc,opentime,price,wayto,re_time,alias,\
            beencounts,source_id)

    #进行插库
    print 'insert',insert_db(tuple)
    return dict


def insert_db(args):
    #sql = 'update mafengwo_0618 set source = %s,name = %s,name_en = %s,map_info = %s,address = %s,star = %s,'+\
    sql = 'update mafengwo_0618 set source = %s,address = %s,star = %s,'+\
            'commentcounts = %s,grade = %s,phone = %s,site = %s,imgurl = %s,introduction = %s,opentime = %s,price = %s,wayto = %s,'+\
            'recommended_time = %s,alias = %s,beentocounts = %s '+\
            'where id = %s' 
    return db_add.ExecuteSQL(sql,args)

def get_url():
    #sql = 'select url from mafengwo where id = \"6325563\"'
    sql = "select * from mafengwo_0618 where address is null or address = ''"
    #sql = "select * from mafengwo_051702 where id in('4660706','6628590','3246','7919')"
    result = db_add.QueryBySQL(sql)
    return result

if __name__ == '__main__':
    #crawl_page('http://www.mafengwo.cn/poi/6542932.html')

    #content = open('mafengwo.html').read()
    #print 
    #mafengwo_parser(content)
    #url = 'http://www.mafengwo.cn/poi/5833771.html'
    #a = MafengwoParser()
    #a.mafengwo_crawl(url)
    #task = 'http://www.mafengwo.cn/poi/5504662.html'
    #task = 'http://www.mafengwo.cn/poi/6933436.html'
    s = MafengwoParser()
    #s.crawl(task)
    for i in get_url():
        task =  i['url']
        print task
        s.crawl(task)
        time.sleep(2)
 
    #content = open('mafengwo.html').read()
    #print page_parser(content,task)
    #f = codecs.open('page.json','r','utf-8')
    #page_list = f.readlines()
    #for i in range(0,70001,10000):
    #    file = '/data/yanlihua/mafengwo_page/mafengwo_url%s.json' % i
    #    print 'file: %s' % file
    #    for each in open(file).readlines():
    #        try:
    #            page = json.loads(each[each.find('{'):])
    #            content = page['content']
    #            url = page['url']
    #            print '----- %s ----' % url
    #            page_parser( content, url )
    #        except Exception,e:
    #            print str(e)
    #            continue
    '''
    task = 'ma_052502'
    page_nums = get_mongo.get_nums( task )
    print 'all page:%s' % page_nums
    offset = 1
    limit_count = 1
    while offset <= page_nums:
        print 'offset: %s' % offset
        try:
            page = get_mongo.read_content( task, offset, limit_count )
            content = page['content']
            #open('test.html','w').write(content)
            url = page['url']
            print '--------------------- offset: %s ------------------------' % offset
            if len(content)>1000:
                result =  parse( content, url )
        except Exception,e:
            print 'parse error in page %s' % offset
            print str(e)
        offset += 1
    print '%s rest over' % str(offset-1)
    '''
