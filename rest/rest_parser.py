#! /usr/bin/env python
#coding=utf-8
"""
    @desc: 抓取tripadvisor餐厅详情页，需要提供餐厅URL
"""
from util.Browser import MechanizeCrawler as MC
from common.common import get_proxy,invalid_proxy
import json
from lxml import html
import re
import db_add
import get_mongo
import all_comment
import os
import sys
import time


reload(sys)
sys.setdefaultencoding('utf-8')

TASK_TABLE = 'tp_rest_basic_0707'
p = get_proxy(source = 'Platform')

def get_task():
    sql = 'select res_url from '+TASK_TABLE+" where map_info ='' or map_info='NULL' map_info is null"
    return db_add.QueryBySQL(sql)

def has_chinese(contents,encoding='utf-8'):
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    if not isinstance(contents,unicode):
        u_contents = unicode(contents,encoding=encoding)
    results = zh_pattern.findall(u_contents)
    if len(results) > 0:
        return True
    else:
        return False

def crawl(url):
    global p
    mc = MC()
    #mc.set_debug(True)
    mc.set_proxy(p)
    print 'proxy: %s' % p
    content = ''
    content = mc.req('get', url, html_flag = True,time_out=15)
    count = 0
    while len(content) <1000:
        invalid_proxy(p,'Platform')
        p = get_proxy(source = 'Platform')
        mc.set_proxy(p)
        print 'proxy: %s' % p
        content = mc.req('get', url, html_flag = True,time_out=15)
        count += 1
        if count > 8:
            break
    return content

def parse(content, url):
    print 'url: %s' % url
    rest_info = []
    content = content.decode('utf-8')
    root = html.fromstring(content)

    # id等信息,source_id, source_city_id, soruce
    source_id = re.compile(r'd(\d+)').findall(url)[0]
    #source_id = rest_id

    source = 'daodao'

    # 名字 name,name_en
    try:
        name_en = root.find_class('heading_name_wrapper')[0].text_content().encode('utf-8').strip().split('\n')[1]
    except:
        name_en = ''

    try:
        try:
            name = root.find_class('heading_name_wrapper')[0].text_content().encode('utf-8').strip()
        except:
            name = root.get_element_by_id('HEADING').text_content().encode('utf-8').strip()
        if len( name.split('\n') ) > 1:
            if name.find('停业') > -1 or name.find('移除') > -1:
                print 'stop:',source_id,'\t',url
                raise Exception
            else:
                name = name.split('\n')[0]
    except Exception, e:
            name = ''
            print 'name error',url
            #print str(e)
            # 若出错则返回空的list
            return rest_info

    if name =='' and name_en != '':
        name = name_en
    if name == '' and name_en == '':
        print 'no name'
        #return rest_info
    if name_en =='':
        if not has_chinese(name):
            name_en = name
        else:
            name_en = ''
    # 如果name是英文，则name_en=name
    if not has_chinese(name):
        name_en = name

    print 'name: %s' % name
    print 'name_en: %s' % name_en

    # 经纬度map_info
    try:
        map_info = ''
        if not map_info:
            try:
                lng = root.xpath('//div[@class="mapContainer"]/@data-lng')[0]
                lat = root.xpath('//div[@class="mapContainer"]/@data-lat')[0]
                map_info = str(lng) + ',' + str(lat)
            except:
                map_info = ''

        if not map_info:
            try:
                map_temp = re.compile(r'staticmap\?location=(.*?)&zoom').findall(content)[0]
                map_info = map_temp
            except:
                try:
                    map_temp = re.compile(r'&center=(.*?)&maptype').findall(content)[0]
                    map_infos = map_temp.split(',')
                    map_info = map_infos[1] + ',' + map_infos[0]
                except:
                    try:
                        map_temp = re.compile(r'desktop&center=(.*?)&zoom',re.S).findall(content)[0]
                        map_infos = map_temp.split(',')
                        map_info = map_infos[1] + ',' + map_infos[0]
                    except:
                        map_temp = ''
        if not map_info:
            map_info = ''
    except Exception, e:
        map_info = ''
        print 'map_info error',url
        print str(e)
        return rest_info
    print 'map: %s' % map_info

    # 地址address
    try:
        address = ''
        address = root.find_class('format_address')[0].text_content().strip().encode('utf-8').replace('地址: ','')
    except Exception, e:
        address = ''
        #traceback.print_exc(e)
    print 'address: %s' % address

    # 电话tel
    try:
        tel = root.find_class('fl phoneNumber')[0].text
    except:
        tel = ''
    print 'tel: %s' % tel

    # 排名rank
    try:
        rank = ''
        rank_text = root.find_class('slim_ranking')[0].text_content().encode('utf-8').replace(',','')
        nums = re.compile(r'(\d+)', re.S).findall(rank_text)
        #orank = nums[0] + '/' + nums[1]
        rank = nums[1]
    except Exception, e:
        #traceback.print_exc(e)
        rank = '2000000'
    print 'rank: %s' % rank

    # 评分rating
    try:
        if len(root.find_class('rs rating')) != 0:
            grade_temp = root.find_class('rs rating')[0]
            rating = float(grade_temp.xpath('span/img/@content')[0])
            reviews = int(grade_temp.xpath('a/@content')[0])
        else:
            rating = -1
            reviews = -1
    except Exception, e:
        #traceback.print_exc(e)
        rating = -1
        reviews = -1
    print 'rating: %s' % rating
    print 'reviews: %s' % reviews

    # 开店时间 open_time
    try:
        days = []
        hours = []
        if len( root.find_class('hoursOverlay') ) != 0 :
            for i in root.find_class('hoursOverlay')[0].find_class('days'):
                if len(i.xpath('text()')) != 0:
                    days.append( i.xpath('text()')[0].encode('utf-8').strip() )
            for j in root.find_class('hoursOverlay')[0].find_class('hours'):
                if len(j.xpath('text()')) != 0:
                    hours.append( j.xpath('text()')[0].encode('utf-8').strip() )
        time = ''
        for n in range(len(days)):
            time += days[n]
            time += ' '
            time += hours[n]
            if (n != len(days)-1):
                time += '|'
        if time != '':
            open_time = time
        else:
            open_time = ''

        #if len( root.find_class('hoursOverlay') ) != 0 :
        #    open_time = root.find_class('hoursOverlay')[0].text_content().encode('utf-8')
    except Exception,e:
        #traceback.print_exc(e)
        open_time = ''
    print 'open_time: %s' % open_time


    # 菜式 cuisines
    try:
        cuisines = ''
        cuisines = root.find_class('heading_details')[0].text_content().strip().encode('utf-8').split('\n')[-1].replace(', 更多','').replace(',','|')
    except Exception,e:
        cuisines = ''
    if cuisines.find('+新增菜系') > -1:
        cuisines = ''
    print 'cuisines: %s' % cuisines


    # 评级 rating_by_category
    try:
        temp = []
        for row in root.find_class("ratingRow wrap"):
            try:
                label = row.xpath('div[1]/span/text()')[0].encode('utf-8')
                score_tmp = re.compile(r's(\d+)').findall( row.xpath('div[2]/span/img/@class')[0] )[0]
                score = ".".join(score_tmp)
                temp.append( label + ":" + score )
            except Exception,e:
                continue
        if temp != []:
            rating_by_category = '|'.join(temp)
        else:
            rating_by_category = ''
    except Exception,e:
        #traceback.print_exc(e)
        rating_by_category = ''
    print 'rating_by_category: %s' % rating_by_category

    # 用餐选择 dining_options
    # 价格 price
    # 氛围类别 feature
    try:
        price = ''
        feature = ''
        dining_options = ''
        infos = root.find_class('details_tab')[0].find_class('table_section')[0].find_class('row')
        rows = []
        for info in infos:
            row = info.text_content().encode('utf-8').strip()
            if  row.find('价格') > -1:
                price = info.find_class('content')[0].text_content().encode('utf-8').strip().replace('\n','')
            if  row.find('用餐选择') > -1:
                dining_options = info.find_class('content')[0].text_content().encode('utf-8').strip().replace('\n','')
            if  row.find('氛围类别') > -1:
                feature = info.find_class('content')[0].text_content().encode('utf-8').strip().replace('|','')

    except Exception,e:
        print str(e)
        price = ''
        feature = ''
        dining_options = ''

    print 'price:',price
    print 'feature:',feature
    print 'dining_options:',dining_options
    desc = ''
    menu = ''
    service = ''
    payment = ''


    rest_info = (name, tel, map_info, address, open_time, rating, rank, cuisines, dining_options, reviews, rating_by_category, menu,price,desc,service,payment,source_id )
    result = insert_db(rest_info)
    print 'update basic',result
    return result


def insert_db(args):
    sql = 'update '+TASK_TABLE+' set name=%s,telphone=%s,map_info=%s,address=%s,open_time=%s,grade=%s,real_ranking=%s,cuisines=%s,dining_options=%s,review_num=%s,rating_by_category=%s,menu=%s,price=%s,description=%s,service=%s,payment=%s where id=%s'
    return db_add.ExecuteSQL(sql,args)

if __name__ == '__main__':
    '''
    task = 'tp_rest_basic_070709'
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
                #comment = all_comment.parse( content, url )
                #print '%s comemnts inserted!!!' % len(comment)
            else:
                pass
        except Exception,e:
            print 'parse error in page %s' % offset
            print str(e)
        offset += 1
    print '%s rest over' % str(offset-1)
    '''
    print 'urls count:',len(get_task())
    count = 0
    for i in get_task():
        print '------------------- count: %s --------------------' % count
        url = i['res_url']
        try:
            content = crawl(url)
            if len(content)>1000:
                result = parse( content,url )
                comment = all_comment.parse( content,url )
        except Exception,e:
            print 'parse error in page %s' % count
        count += 1
    print '%s over' % str(count-1)
