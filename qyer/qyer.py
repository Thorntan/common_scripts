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
from logger import logger
import json

reload(sys)
sys.setdefaultencoding('utf-8')

CONTENT_LEN = 100
map_pat = re.compile('png\|(.*)&sensor')

class QyerParser():

    def __init__(self):
        pass

    #def crawl(self,task):
    #
    #    info = qyer_crawl(task)
    #    return info


    def crawl(self,url,uid):
    
        ''' 
        根据任务获取所需网页
        '''
        flag = 1 
        mc = MC()
        #mc.set_debug(True)
        for i in range(3):
            page = mc.req('get',url,html_flag = True)
            if page[0]>CONTENT_LEN:
                break
        _content = page[0]
        _error = page[1]
        info = page_parser(_content,url,uid)
        return info

def page_parser(content,url,uid):
    
    result = {}
    root = HTML.fromstring(content.decode('utf-8'))
    grade = -1
    name = ''
    namm_en = ''
    map_info = ''
    source = 'qyer'

    try:
        source_id = root.xpath('//*[@class="poiDet-handler"]/@data-pid')[0].encode('utf-8').strip()
    except Exception,e:
        logger.info('can not get source_id',str(e))
        source_id = 'NULL'

        result['status'] = 1
        result['content'] = {}
        return result
    
    try:
        source_city_id = re.compile(r'PLACE\.CITYID = "(\d+)";').findall(content)[0]
    except Exception,e:
        source_city_id = 'NULL'

    try:
        name_en = root.xpath('//h1 [@class= "en"]/a/text()')[0].encode('utf-8').strip()
        if name_en.strip():
            pass
        else:
            name_en = "NULL"
    except Exception,e:
        name_en = 'NULL'

    try:
        name = root.xpath('//h1 [@class= "cn"]/a/text()')[0].encode('utf-8').strip()
        if name.strip():
            pass
        else:
            name = name_en
    except Exception,e:
        name = name_en

    
    try:
        map = root.xpath('//div [@class="map"]/img/@src')[0].encode('utf-8').strip()
        map_info = map_pat.findall(map)[0]
        map_info = map_info.split(',')[1] +','+ map_info.split(',')[0]
    except Exception,e:
        logger.info('can not get map_info',str(e))
        map_info = 'NULL'

        result['status'] = 1
        result['content'] = {}
        return result
    

    img_url = url +'photo/'

    try:
        grade_root = root.find_class('infos')[0].find_class('points')[0].find_class('number')
        if len(grade_root) != 0:
            grade = root.find_class('infos')[0].find_class('number')[0].text_content().encode('utf-8').strip()
            if len(grade) == 0 or grade.find('暂无评分') > -1:
                grade = -1
            else:
                pass
        else:
            grade = -1
    except Exception, e:
        grade = -1
    
    try:
        star_root = root.find_class('infos')
        count_tmp = star_root[0].find_class('summery')[0].text_content().encode('utf-8').strip()
        star_list0 = star_root[0].find_class('single-star full')
        star_list1 = star_root[0].find_class('single-star half')
        star = len(star_list0)*1 + len(star_list1)*0.5
        if star == 0:
            star = -1
        comments = count_tmp.split('条')[0]
        if len(comments) == 0 or comments.find('暂无评分') > -1:
            comments = -1
        else:
            pass
    except Exception, e:
        star = -1

    try:
        rank = 'NULL'
        rank_tmp = root.find_class('infos')[0].find_class('rank')[0].xpath('./span/text()')[0].encode('utf-8').strip()
        rank_pat = re.compile(r'第(\d*)名',re.S)
        rank = rank_pat.findall(rank_tmp)[0]
        if len(rank) == 0:
            rank = 'NULL'
    except Exception, e:
        rank = 'NULL'

    try:
        header = root.find_class('infos')[0].find_class('rank')[0].text_content().encode('utf-8').strip()
        if header.find('购物') > -1:
            cateid = '购物'
        elif header.find('美食') > -1:
            cateid = '美食'
        elif header.find('景点') > -1:
            cateid = '景点'
        elif header.find('活动') > -1:
            cateid = '活动'
        elif header.find('交通') > -1:
            cateid = '交通'
        else:
            cateid = '其他'
    except Exception,e:
        cateid = 'NULL'

    #details对应数据库中的tips
    try:
        main_detail = root.find_class('poiDet-detail')[0].xpath('text()')[0].encode('utf-8').strip()
        if len(root.find_class('poiDet-showtar')) != 0:
            more_detail = root.find_class('poiDet-showtar')[0].xpath('p/text()')[0].encode('utf-8').strip()
        else:
            more_detail = ''
        detail = main_detail + more_detail
    except Exception, e:
        detail = 'NULL'
    

    try:
        beentocount = root.find_class('golden')[0].text_content().encode('utf-8').strip()
    except Exception,e:
        beentocount = -1


    price = 'NULL'
    wayto = 'NULL'
    opentime = 'NULL'
    address = 'NULL'
    phone = 'NULL'
    site = 'NULL'
    tagid = 'NULL'
    tips_root = root.find_class('poiDet-tips')[0].xpath('./li')
    for every in tips_root:
        title = every.find_class('title')[0].text_content().encode('utf-8').strip()[:-3]
        content = every.find_class('content')[0].text_content().encode('utf-8').strip()
        if title =='门票':
            price = content
        if title == '到达方式':
            wayto = content
        if title =='开放时间':
            opentime = content.strip().replace('\n',',').replace('\t','')
        if title == '营业时间':
            opentime = content.strip().replace('\n',',').replace('\t','').replace('  ','')
        if title =='地址':
            address = content.replace('(查看地图)',' ').strip()
        if title == '电话':
            phone = content
        if title =='网址':
            site = content
        if title =='所属分类':
            tagid = content
    try:
        tip = root.xpath('//div [@class="poiDet-tipContent"]/div/p/text()')[0]
        tip = tip.encode('utf-8').strip()
    except:
        tip = 'NULL'

    try:
        if (source_city_id != 'NULL'):
            c = get_city(source_city_id)[0]
            source_country_id = c['source_country_id']
            source_city_name = c['source_city_name'].encode('utf-8')
            source_city_name_en = c['source_city_name_en'].encode('utf-8')
            source_country_name = c['source_country_name'].encode('utf-8')
        else:
            source_city_name = 'NULL'
            source_city_name_en = 'NULL'
            source_country_name = 'NULL'
            source_country_id = 'NULL'
    except Exception,e:
        source_city_name = 'NULL'
        source_city_name_en = 'NULL'
        source_country_name = 'NULL'
        source_country_id = 'NULL'

    data = (source_id,source,source_city_id,source_city_name,source_city_name_en,source_country_id,source_country_name,name,name_en,map_info,address,star,beentocount,rank,comments,tip,tagid,grade,phone,site,img_url,detail,opentime,price,wayto,cateid,url,uid) #uid
        
    info = {
            'source_id':source_id,
            'source':source,
            'source_city_id':source_city_id,
            'source_city_name':source_city_name,
            'source_city_name_en':source_city_name_en,
            'source_country_id':source_country_id,
            'name':name,
            'name_en':name_en,
            'map_info':map_info,
            'address':address,
            'star':star,
            'beentocount':beentocount,
            'ranking':rank,
            'commentcounts':comments,
            'tip':tip,
            'tagid':tagid,
            'grade':grade,
            'phone':phone,
            'site':site,
            'img_url':img_url,
            'desc':detail,
            'opentime':opentime,
            'price':price,
            'wayto':wayto,
            'cateid':cateid,
            'miaoji_id':uid,
            'url':url
            }

    insert_attr(data)
    logger.info('insert data !!!')
    result['status'] = 0
    result['content'] = str(info)
    return result

def get_city(args):
    sql = 'select * from qyer_city where source_city_id=\'%s\'' % args
    return db_add.QueryBySQL(sql)

def insert_attr(args):
    sql = 'insert ignore into attr_test(id,source,source_city_id,source_city_name, source_city_name_en,source_country_id,source_country_name,name,name_en,map_info,address,star,beentocounts,ranking,commentcounts,tips,tagid,grade,phone,site,imgurl,introduction,opentime,price,wayto,cateid,url,miaoji_id) values( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' # on duplicate key update cateid=values(cateid)'
    db_add.ExecuteSQL(sql,args)


if __name__ == '__main__':

    s = QyerParser()
    task = 'http://place.qyer.com/poi/V2UJYlFmBzBTZFI7/'
    url = 'http://place.qyer.com/poi/V2cJZ1FmBzZTYw/'
    url = 'http://place.qyer.com/poi/V2UJY1FmBzRTY1I-/'
    url = 'http://place.qyer.com/poi/V2UJY1FiBzBTYFI-/'
    url = 'http://place.qyer.com/poi/V2UJYlFnBzRTbVI-/'
    uid = 'v00000001'
    r =  s.crawl( url,uid )
    a = eval(r['content'])
    for k,v in a.iteritems():
        print k,v
    
    #task = 'http://place.qyer.com/poi/V2cJa1FiBz5TZA/'
