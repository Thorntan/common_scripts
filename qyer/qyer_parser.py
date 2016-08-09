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

# -------------------------------

# 需要更新的表
BASIC_TABLE = 'qyer_outlets'
# 链接任务表格
TASK_TABLE = 'qyer_outlets'
# 是否入库,True为入库，False为不入库
IS_INSERT = False
# 调试，如果为True仅调试一个URL就break
DEBUG = True
# ---------------------------------


def get_task():
    #sql = 'select * from '+TASK_TABLE+' where source_country_id=\'14\' and cateid=\'景点\''
    #sql = "select * from "+TASK_TABLE+" where source_city_id in('8858','8804','9820','9818','7454','9815','9954','9933')"
    sql = "select * from "+TASK_TABLE+" where map_info is null "
    return db_add.QueryBySQL(sql)


class QyerParser():

    def __init__(self):
        pass

    def crawl(self,url):

        crawl_flag = self.qyer_crawl(url)
        return crawl_flag


    def qyer_crawl(self,url):

        '''
        根据任务获取所需网页
        '''
        flag = 1
        mc = MC()
        #mc.set_debug(True)
        for i in range(3):
            page = mc.req('get',url,html_flag = True)
            if page[0]>100:
                break
        _content = page[0]
        _error = page[1]
        '''
        fout = open('qyer.html','w')
        fout.write(_content)
        fout.close()
        '''
        try:
            info = page_parser(_content,url)
            #logger.info('Parser Finish [%s] [%s] [%s] [%s] [%s] [%s]'%(info))
            return info
        except Exception,e:
            print traceback.print_exc()
            #logger.info('Parser Failed')
            return 1

def page_parser(content,url):

    dict = {}
    root = HTML.fromstring(content.decode('utf-8'))
    score = -1
    name = ''
    namm_en = ''
    map_info = ''
    source = 'qyer'
    #try:
    #    #header = root.find_class('qyer_head_crumbg')[0].text_content().encode('utf-8').strip()
    #    header = root.find_class('qyer_head_crumb')[0].text_content().encode('utf-8').strip()
    #    if header.find('购物') > -1:
    #        cateid = '购物'
    #    elif header.find('美食') > -1:
    #        cateid = '美食'
    #    elif header.find('景点') > -1:
    #        cateid = '景点'
    #    else:
    #        cateid = '其他'
    #except Exception,e:
    #    cateid = 'NULL'

    try:
        source_id = root.xpath('//div [@class="poiDet-tars clearfix"]/div[2]/div/@poiid')[0]
        source_id = source_id.encode('utf-8').strip()
    except Exception,e:
        print str(e)
        source_id = 'NULL'
    print 'source_id'
    print source_id
    try:
        name_en = root.xpath('//h1 [@class= "en"]/a/text()')[0].encode('utf-8').strip()
        if name_en.strip():
            pass
        else:
            name_en = "NULL"
    except Exception,e:
        print str(e)
        name_en = 'NULL'

    try:
        name = root.xpath('//h1 [@class= "cn"]/a/text()')[0].encode('utf-8').strip()
        if name.strip():
            pass
        else:
            name = name_en
    except Exception,e:
        print str(e)
        name = name_en

    print 'name_en'
    print name_en
    print 'name'
    print name
    #logger.info("name:%s"%(name))

    try:
        map = root.xpath('//div [@class="map"]/img/@src')[0].encode('utf-8').strip()
        map_info = re.compile('png\|(.*)&sensor').findall(map)[0]
        map_info = map_info.split(',')[1] +','+ map_info.split(',')[0]
    except Exception,e:
        print str(e)
        map_info = 'NULL'
    print 'map_info'
    print map_info

    img_url = url +'photo/'

    try:
        score_root = root.find_class('infos')[0].find_class('points')[0].find_class('number')
        if len(score_root) != 0:
            score = root.find_class('infos')[0].find_class('number')[0].text_content().encode('utf-8').strip()
            if len(score) == 0 or score.find('暂无评分') > -1:
                score = -1
            else:
                pass
        else:
            score = -1
    except Exception, e:
        print str(e)
        score = -1

    print 'score'
    print score
    #comments = -1
    try:
        star_root = root.find_class('infos')
        count_tmp = star_root[0].find_class('summery')[0].text_content().encode('utf-8').strip()
        star_list0 = star_root[0].find_class('single-star full')
        star_list1 = star_root[0].find_class('single-star half')
        star = len(star_list0)*2 + len(star_list1)*1
        star = float(float(star)/2)
        if star == 0:
            star = -1
        comments = count_tmp.split('条')[0]
        if len(comments) == 0 or comments.find('暂无评分') > -1:
            comments = -1
        else:
            pass
    except Exception, e:
        print str(e)
        star = -1
    print 'star'
    print star
    try:
        rank = 'NULL'
        rank_tmp = root.find_class('infos')[0].find_class('rank')[0].xpath('./span/text()')[0].encode('utf-8').strip()
        rank_pat = re.compile(r'第(\d*)名',re.S)
        rank = rank_pat.findall(rank_tmp)[0]
        if len(rank) == 0:
            rank = '2000000'
        else:
            pass
    except:
        rank = ''
    print 'rank'
    print rank
    #details对应数据库中的tips
    try:
        main_detail = root.find_class('poiDet-detail')[0].xpath('text()')[0].encode('utf-8').strip()
        if len(root.find_class('poiDet-showtar')) != 0:
            more_detail = root.find_class('poiDet-showtar')[0].xpath('p/text()')[0].encode('utf-8').strip()
        else:
            more_detail = ''
        detail = main_detail + more_detail
    except Exception, e:
        #logger.info('%s', e)
        detail = 'NULL'
        print str(e)

    print 'details'
    print detail

    try:
        beentocount = root.find_class('golden')[0].text_content().encode('utf-8').strip()
    except Exception,e:
        beentocount = -1
        print str(e)

    print 'beentocount'
    print beentocount

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
            print price
        if title == '到达方式':
            wayto = content
        if title =='开放时间':
            opentime = content.replace('\n',',')
        if title == '营业时间':
            opentime = content
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
    print 'site'
    print site
    print 'wayto'
    print wayto
    print 'open-time'
    print opentime
    print 'tip'
    print tip
    print 'address'
    print address
    print 'price'
    print price
    print 'tagid'
    print tagid

    #print 'cateid'
    #print cateid

    data = ()
    #if map_info=='NULL':
    #    return data
    #data_insert = (name,name_en,map_info,address,star,beentocount,rank,comments,tip,tagid,score,phone,site,img_url,detail,opentime,price,wayto,url)
    data = (name,name_en,map_info,address,star,beentocount,rank,comments,tip,tagid,score,phone,site,img_url,detail,opentime,price,wayto,url)
    if IS_INSERT:
        #print 'insert',insert_db(data)
        print 'update',update_db(data)
    return data

def update_db(args):
    sql = 'update '+BASIC_TABLE+' set name=%s,name_en=%s,map_info=%s,address=%s,star=%s,beentocounts=%s,ranking=%s,commentcounts=%s,tips=%s,tagid=%s,grade=%s,phone=%s,site=%s,imgurl=%s,introduction=%s,opentime=%s,price=%s,wayto=%s where url=%s'
    return db_add.ExecuteSQL(sql,args)

def insert_db(args):
    sql = 'replace into qyer_japan(id,source,source_city_id,source_city_name, source_city_name_en,source_country_id,source_country_name,name,name_en,map_info,address,star,beentocounts,ranking,commentcounts,tips,tagid,grade,phone,site,imgurl,introduction,opentime,price,wayto,cateid,url) values( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    return db_add.ExecuteSQL(sql,args)

if __name__ == '__main__':

    s = QyerParser()
    count = 0
    for task in get_task():
        print 'count:',count
        url = task['url']
        try:
            print url
            s.crawl(url)
        except:
            print 'error:',url
        count += 1
        if DEBUG:
            break
    print count,'over'

