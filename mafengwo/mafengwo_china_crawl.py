# coding=utf-8
'''
    @author:    yanlihua
    @date:      2015-10-16
    @desc:      马蜂窝中国景点URL的抓取
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

# 得到全国省份id >>  城市id >> 景点id

def insert_db(id,source,source_country_id,source_city_id,url):
    sql="replace into mafengwo_china_by_province(id,source,source_country_id,source_city_id,url) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (id,source,source_country_id,source_city_id,url)
    db_add.ExecuteSQL(sql)

def get_sight():
    source = 'mafengwo_crawl'
    source_country_id  = '21536'
    mc = MC()
    #mc.set_debug(True)

    # 从首页中得到所有province的id
    url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid='+ str(source_country_id) + '&iType=3&iPage=1'
    page_province = mc.req('get',url,html_flag=True)
    province_ids = []
    data = json.loads(page_province)
    for province in data['list']:
        province_ids.append(str(province['id']))
    
    # 直辖市和特别行政区列表
    special_city_list = ['10208','10320','10099','10065','10189','10206']
    
    # 遍历每个省份的城市
    for source_province_id in province_ids:
        # 如果id是特殊城市，则跳过
        #if (source_province_id in special_city_list):
            #continue
        # 得到该province的城市列表
        ajax_url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid='+ str(source_province_id) + '&iType=3&iPage=1'
        print "--------%s-------" % ajax_url
        try:
            city_ids = []
            if (source_province_id in special_city_list):
                city_ids.append(source_province_id)
            else:
                page3 = mc.req('get',ajax_url,html_flag=True)
                data = json.loads(page3)
                for city in data['list']:
                    source_city_id = str(city['id'])
                    city_ids.append(source_city_id)
            #print len(city_ids)
            for source_city_id in city_ids:
                print source_city_id
                # 得到这个城市的所有景点
                city_url = "http://www.mafengwo.cn/jd/"+ source_city_id +"/gonglve.html"
                print "----------------%s-----------------" % city_url
                try:
                    content = mc.req('get',city_url,html_flag=True)
                    tree = etree.HTML(content)
                    # 判断该city是否有景点
                    is_no_sight = re.compile(r'没有景点').findall(content)
                    if (len(is_no_sight) != 0):
                        print "%s no sights!!!!!!!!!!!!!!!" % source_city_id
                    else:
                        sight_counts = len(tree.xpath('//*[@class="list"]/ul/li'))
                        if (sight_counts == 0):
                            # 景点数目较少时，景点列表可以在前面得到
                            #sight_counts = len(tree.xpath('//*[@class="poi-list"]/li'))
                            # 如果景点页面超过一页
                            page = 1
                            next_page = 1
                            sum = 0
                            while (next_page == 1):
                                if (page != 1):
                                    url = "http://www.mafengwo.cn/jd/"+source_city_id+"/0-0-0-0-0-"+str(page)+".html"
                                    content = mc.req('get',url,html_flag=True)
                                    tree = etree.HTML(content)
                                next_page = len(re.compile(r'>(后一页)<').findall(content))
                                sight_counts = len(tree.xpath('//*[@class="poi-list"]/li'))
                                sum += int(sight_counts)
                                for n in range(1,sight_counts+1):
                                    sight_path = tree.xpath('//*[@class="poi-list"]/li[%s]/div[2]/h3/a/@href' % n)[0].strip().encode('utf-8')
                                    sight_id = re.compile(r'(\d+)').findall(sight_path)[0].encode('utf-8')
                                    sight_url = "http://www.mafengwo.cn"+sight_path
                                    print sight_id,sight_url
                                    insert_db(sight_id, source, source_country_id, source_city_id, sight_url)
                                next_page = len(re.compile(r'>(后一页)<').findall(content))
                                page +=1
                            print "%s sight counts: %s" % (source_city_id,sum)
                        else:
                            # 很多景点的情况，从页面最底下的列表可以得到所有的景点链接
                            sight_counts = len(tree.xpath('//*[@class="list"]/ul/li'))
                            print "sight counts: %s" % sight_counts
                            for m in range(1,sight_counts+1):
                                sight_path = tree.xpath('//*[@class="list"]/ul/li[%s]/a/@href' % m)[0].strip().encode('utf-8')
                                sight_id = re.compile(r'(\d+)').findall(sight_path)[0].encode('utf-8')
                                sight_url = "http://www.mafengwo.cn"+sight_path
                                print sight_id,sight_url
                                insert_db(sight_id, source, source_country_id, source_city_id, sight_url)
                            print "%s sight counts: %s" % (source_city_id,sight_counts)
                except Exception,e:
                    print "error: %s" % city_url
                    print str(e)
                    continue

                # 至此得到一个城市的景点

            # 打印该province的city数目
            print "province: %s city counts: %s" % (source_province_id,len(city_ids))
        except Exception,e:
            print "error: %s" % source_province_id
            print str(e)
            continue
    
if __name__ in '__main__':
    get_sight()
    print "all over"
