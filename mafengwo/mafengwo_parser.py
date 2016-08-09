#!/usr/bin/env python
# coding=utf-8
'''
    @author:    yanlihua
    @date:      2015-10-16
    @desc:      马蜂窝所有景点页面的抓取和解析
    @update:    2015-10-16
'''
import lxml.html as HTML
import re
import traceback
from util.Browser2 import MechanizeCrawler as MC 
#from util.Browser import MechanizeCrawler as MC 
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
        #mc.set_debug(True)
        #p = get_proxy(source='Platform')
        #p = '1.173.108.243:8088'
        #mc.set_proxy(p)
        page = mc.req('get',url,html_flag = True)
        _content = page[0]
        _err = page[1]
        fout = open('mafengwo.html','w')
        fout.write(_content)
        fout.close()
        
        try:
            info = page_parser(_content,url)
            #logger.info('Parser Finish [%s] [%s] [%s] [%s] [%s] [%s]'%(info))
            return 0,info
        except:
            print traceback.print_exc()
            #logger.info('Parser Failed')
            return 1,info


def page_parser(content,url):
    
    dict = {}
    attr_list = []
    alias = 'NULL'
    name_en = 'NULL'
    nearby_id = ''
    source_id = 'NULL'
    address = ''
    source_id = url.split('/')[4].replace('.html','')
    print source_id
    root = HTML.fromstring(content.decode('utf-8'))
    try:
        name_zh = root.xpath('//div[@class="s-title"]/h1/text()')[0]
        name_zh = name_zh.strip().encode('utf-8')
    except:
        try:
            name_zh = root.xpath('//div [@class="title clearfix"]/div[1]/h1/text()')[0]
            name_zh = name_zh.encode('utf-8').strip()
        except Exception,e:
            name_zh = 'NULL'
    print 'name_zh'
    print name_zh
    
    try:
        t_name_en = root.xpath('//div [@class="s-title"]/p/span/text()')[0]
        name_en = t_name_en.strip().encode('utf-8').replace('（','').replace('）','').replace("'","''")
    except:
        try:
            t_name_en = root.xpath('//div [@class="title clearfix"]/text()')[0]
            t_name_en = t_name_en.encode('utf-8').strip().replace("'","''")
        except Exception,e:
            print str(e)
            name_en = 'NULL'
    print 'name_en'
    print name_en
    try:
        img_url = root.xpath('//a [@class="photo"]/@href')[0].encode('utf-8').strip()
        img_url = 'http://www.mafengwo.cn' + img_url
    except:
        try:
            img_url = root.xpath('//div[@class="pic-r"]/a/@href')[0].encode('utf-8').strip()
            img_url = 'http://www.mafengwo.cn' + img_url
        except Exception,e:
            print str(e)
            img_url = 'NULL'
    
    print 'img_url'
    print img_url
    
    try:
        t_ranking = root.xpath('//div [@class="ranking"]/em/text()')[0]
        ranking = rank_pat.findall(t_ranking)[0]
    except:
        ranking = 'NULL'

    print 'ranking'
    print ranking
    try:
        grade = root.find_class('txt-l')[0].xpath('div[1]/span/em/text()')[0].strip()
    except Exception, e:
        grade = 'NULL'
    
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
        address = address.strip().encode('utf-8').replace("'","''")
    except:
        try:
            address = root.xpath('//div[@class="col-side _j_rside"]/div[3]/ul/li[1]/text()')[0]
            address = address.encode('utf-8').strip().replace("'","''")
        except Exception,e:
            print str(e)
            address = 'NULL'
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
        been_nums = root.xpath('//div[@class="m-box m-been"]/ul/li')
        beencounts = int(len(been_nums))
    except:
        beencounts = -1
    print 'beencounts'
    print beencounts
    try:
        desc = root.xpath('//div [@class="row row-overview"]/div[4]/dl/dt/p/span/text()')[0]
        desc = desc.encode('utf-8').strip().replace("'","''")
    except Exception,e:
        print str(e)
        desc = 'NULL'
    print 'desc'
    print desc
    
    phone = 'NULL'
    site = 'NULL'
    wayto = 'NULL'
    price = 'NULL'
    opentime = 'NULL'
    re_time = 'NULL'
    alias = 'NULL'
    try:
        info_list = root.xpath('//div [@class="row row-overview"]/div[4]/dl/dd')
        info_dict = {}    
        if info_list != []:
            for x in info_list:
                try:
                    info_key = x.xpath('./span/text()')[0].encode('utf-8').strip()
                    if '电话' in info_key:
                        phone = x.xpath('./p/text()')[0].encode('utf-8').strip()
                    if '网址' in info_key:
                        site = x.xpath('./p/a/text()')[0].encode('utf-8').strip()
                    if '交通' in info_key:
                        wayto = x.xpath('./p/span/text()')[0].encode('utf-8').strip().replace("'","''")
                    if '门票' in info_key:
                        price = x.xpath('./p/span/text()')[0].encode('utf-8').strip()
                    if '开放时间' in info_key:
                        opentime = x.xpath('./p/span/text()')[0].encode('utf-8').strip()
                    if '用时参考' in info_key:
                        re_time = x.xpath('./p/text()')[0].encode('utf-8').strip()
                except Exception,e:
                    print str(e)
                    continue
        if info_list == []:
            try:
                info_path = root.xpath('//div [@class="poi-info poi-base tab-div hide"]')[0]
                try:
                    info_list = info_path.xpath('div[2]/h3')
                    info_dict = {}    
                    for x in info_list:
                        info_key = x.text_content().encode('utf-8').strip()
                        info_value = x.getnext().text_content().encode('utf-8').strip()
                        info_dict[info_key] = info_value
                    print info_dict
                    if '简介' in info_dict.keys():
                        desc = info_dict['简介'].encode('utf-8').replace("'","''")
                    else:
                        desc = 'NULL'

                    if '网址' in info_dict.keys():
                        site = info_dict['网址'].encode('utf-8')
                    else:
                        site = 'NULL'

                    if '电话' in info_dict.keys():
                        phone = info_dict['电话'].encode('utf-8')
                    else:
                        phone = 'NULL'

                    if '交通' in info_dict.keys():
                        wayto = info_dict['交通'].encode('utf-8')
                    else:
                        wayto = 'NULL'
                    
                    if '门票' in info_dict.keys():
                        price = info_dict['门票'].encode('utf-8')
                    else:
                        price = 'NULL'
                    if '英文名称' in info_dict.keys():
                        name_en = info_dict['英文名称'].encode('utf-8')
                    else:
                        name_en = 'NULL'
                    
                    if '当地名称' in info_dict.keys():
                        alias = info_dict['当地名称'].encode('utf-8')
                    else:
                        alias = 'NULL'
                except Exception, e:
                    print str(e)
                    pass

            except Exception,e:
                print str(e)
    except Exception,e:
        print str(e)

    print 'desc'
    print desc
    print 'address'
    print address
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
    print alias
    try:
        map_info_temp = map_pat.findall(content)[0]
        map_info = map_info_temp[1] + ',' + map_info_temp[0]
    except Exception, e:
        map_info = 'NULL'
    print 'map_info'
    print map_info
    
    try:
        telated_pois = root.find_class('row row-scenic')[0].xpath('div/ul/li')
        num = int(len(telated_pois))
        i = 0
        while i<num:
            l = telated_pois[i].xpath('a/@href')[0].encode('utf-8')
            l_result = id_pat.findall(l)[0]
            if i != num-1:
                nearby_id += str(l_result)+'_'
            else:
                nearby_id += str(l_result)
            i+=1
    except:
        nearby_id = 'NULL'
    print 'telate_pois'
    print nearby_id
    source = 'mafengwo'
    name = name_zh
    #name_en = 'NULL'
    name_py = 'NULL'
    city_id = 'NULL'
    md5sum = 'NULL'
    flag = 0
    
    tuple = (source,name,name_en,map_info,address,star,comment_num,grade,phone,site,\
            img_url,desc,opentime,price,wayto,re_time,alias,\
            beencounts,source_id)

    #进行插库
    #insert_db(tuple)

    dict = get_dict(name,name_en,map_info,address,star,comment_num,grade,phone,site,img_url,desc,opentime\
            ,price,wayto,re_time,alias,beencounts,nearby_id)

    return dict

def get_dict(name,name_en,map_info,address,star,commentcounts,grade,phone,site,img_url,desc,opentime\
        ,price,wayto,re_time,alias,beentocounts,related_pois):

    dict = {}
    dict['name'] = name
    dict['name_en'] = name_en
    dict['map_info'] = map_info
    dict['address'] = address
    dict['star'] = star
    dict['commentcounts'] = commentcounts
    dict['grade'] = grade
    dict['phone'] = phone
    dict['site'] = site
    dict['imgurl'] = img_url
    dict['introduction'] = desc
    dict['opentime'] = opentime
    dict['price'] = price
    dict['wayto'] = wayto
    dict['recommended_time'] = re_time
    dict['alias'] = alias
    dict['beentocounts'] = beentocounts
    dict['related_pois'] = related_pois

    return dict

def insert_db(args):
    
    ''' 
    插库函数
    '''
    sql = 'update mafengwo_0517 set source = %s,name = %s,name_en = %s,map_info = %s,address = %s,star = %s,'+\
            'commentcounts = %s,grade = %s,phone = %s,site = %s,imgurl = %s,introduction = %s,opentime = %s,price = %s,wayto = %s,'+\
            'recommended_time = %s,alias = %s,beentocounts = %s '+\
            'where id = %s' 
    #return db_add.ExecuteSQL(sql,args)

def get_url():
    sql = 'select id from mafengwo_0517 order by id'
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
        print '--------------------------'
        #task = 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/%s.html' % i['id']
        task = 'http://www.mafengwo.cn/poi/%s.html' % i['id']
        print task
        s.crawl(task)
        break
 
    #content = open('mafengwo.html').read()
    #print page_parser(content,task)
    #f = codecs.open('page.json','r','utf-8')
    #page_list = f.readlines()
    '''
    for i in range(0,70001,10000):
        file = '/data/yanlihua/mafengwo_page/mafengwo_url%s.json' % i
        print 'file: %s' % file
        for each in open(file).readlines():
            try:
                page = json.loads(each[each.find('{'):])
                content = page['content']
                url = page['url']
                print '----- %s ----' % url
                page_parser( content, url )
            except Exception,e:
                print str(e)
                continue
    '''
