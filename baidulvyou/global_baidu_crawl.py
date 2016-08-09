# coding=utf-8
'''
    @author:    yanlihua
    @date:      2015-10-22
    @desc:      百度旅游国外所有URL的抓取
    @update:    2015-10-28
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

def insert_country_data(source, country_surl, country_name):
    sql="replace into baidu_country(source,source_country_id, source_country_name) values (\'%s\',\'%s\',\'%s\')" % (source, country_surl, country_name)
    db_add.ExecuteSQL(sql)

def insert_city_data(source, country_surl, country_name, city_surl, city_name):
    sql="replace into baidu_city(source,source_country_id, source_country_name, source_city_id, source_city_name) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (source, country_surl, country_name, city_surl, city_name)
    db_add.ExecuteSQL(sql)

def insert_db(id,source,source_country_id,source_city_id,url):
    sql="replace into baidu(id,source,source_country_id,source_city_id,url) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (id,source,source_country_id,source_city_id,url)
    db_add.ExecuteSQL(sql)

def baidulvyou_crawl():
    source = 'baidulvyou'
    mc = MC()
    #mc.set_debug(True)

    index_url = 'http://lvyou.baidu.com/scene'
    index_page = mc.req('get',index_url,html_flag=True)
    open('index.html','w').write(index_page)
    # 一定要使用codecs转码,utf-8,否则乱码
    content = codecs.open('index.html','r','utf-8').read()
    tree = etree.HTML(content)

    continents = tree.xpath('//*[@id="J-head-menu"]/li')
    
    # 遍历每一个大洲，得到每个国家的surl
    country_surls =[]
    country_names = []
    for c in continents[2:]:
        country_list =[]
        area_str = c.xpath('textarea/text()')[0].strip().encode('utf-8')
        area_list = json.loads(area_str) 
        for a in area_list:
            #print a['type'].encode('utf-8') # 大洲的东南西北地区
            country_list = a['sub']
            for country in country_list:
                country_id = country['sid'].encode('utf-8')
                country_name = country['sname'].encode('utf-8') 
                print '-----------------------'
                print country_name.encode('utf-8')
                country_surl = country['surl'].encode('utf-8').replace("'","''") 
                country_names.append( country_name )
                country_surls.append( country_surl )
                #insert_country_data(source, country_id, country_name)
                
                # 得到全国的城市id
                country_url = 'http://lvyou.baidu.com/destination/ajax/jingdian?format=ajax&cid=0&playid=0&seasonid=5&surl='+ str(country_surl) +'&pn=1&rn=2000'#zhongguo city_counts:849
                #print country_url

                # 得到全国的景点
                try:
                    citylist_page = mc.req('get',country_url,html_flag=True)
                    #open('country.json','w').write(citylist_page)
                    citylist_data = json.loads(citylist_page)

                    # 重点！！！获得请求id
                    request_id = citylist_data['data']['request_id']

                    # 城市总数
                    city_total = citylist_data['data']['scene_total']
                    # 翻页数
                    p_total = int(math.ceil(float(city_total)/8))
                    
                    # 国家城市列表翻页
                    for p_num in range(1,p_total+1):
                        country_url = 'http://lvyou.baidu.com/destination/ajax/jingdian?format=ajax&cid=0&playid=0&seasonid=5&surl='+ str(country_surl) +'&pn='+str(p_num)+'&rn=8' #zhongguo city_counts:849
                        citylist_page = mc.req('get',country_url,html_flag=True)
                        open('country.json','w').write(citylist_page)
                        citylist_data = json.loads(citylist_page)
                        # 城市列表
                        city_list = citylist_data['data']['scene_list']

                        # 遍历每个城市
                        for city in city_list:
                            city_id = city['sid'].encode('utf-8')
                            city_name = city['sname'].encode('utf-8')
                            city_surl = city['surl'].replace("'","''")
                            #insert_city_data(source, country_id, country_name, city_id, city_name)

                            print country_name.encode('utf-8'),city_name.encode('utf-8')
                            #city_url = 'http://lvyou.baidu.com/'+ city_surl +'/ditu/' # 地图页面
                            city_url='http://lvyou.baidu.com/destination/ajax/jingdian?format=ajax&rn=8&surl='+ str(city_surl) +'&cid=0&pn='+'1'+'&t='+ str(request_id) 
                            print city_url
                            try:
                                # 得到这个城市的首页
                                sightlist_page = mc.req('get',city_url,html_flag=True)
                                open('city.html','w').write(sightlist_page)
                                sightlist_data = json.loads(sightlist_page)
                                # 景点总数
                                sight_total = sightlist_data['data']['scene_total']
                                print "sight total: %s" % sight_total
                                # 翻页数目
                                page_total = int(math.ceil(float(sight_total)/8))
                                # 景点列表
                                sight_list = sightlist_data['data']['scene_list']

                                # 遍历每一页列表，得到景点url
                                for page_num in range(1,page_total+1):
                                    page_url='http://lvyou.baidu.com/destination/ajax/jingdian?format=ajax&rn=8&surl='+ str(city_surl) +'&cid=0&pn='+ str(page_num) +'&t='+ str(request_id) 
                                    print page_url
                                    scenelist_page = mc.req('get',page_url,html_flag=True)
                                    scenelist_data = json.loads(scenelist_page)
                                    scene_list = scenelist_data['data']['scene_list']
                                    for scene in scene_list:
                                        scene_id = scene['sid'].encode('utf-8')
                                        scene_surl = scene['surl'].replace("'","''")
                                        #print scene_surl
                                        # 景点的URL
                                        scene_url = 'http://lvyou.baidu.com/' + str(scene_surl)
                                        #print scene_url
                                        #insert_db(scene_id, source, country_id, city_id, scene_url)    

                                    # 一页列表到此完成
                            except Exception,e:
                                print "error: %s" % city_surl
                                print str(e)
                                continue
                            #break
                            # 一个城市到此完成
                except Exception,e:
                    # 如果当前国家的抓取抛异常，则跳到下一个国家
                    print "error: %s" % country_surl
                    print str(e)
                    continue
                    #break
                    # 一个城市到此完成

if __name__ in '__main__':
    baidulvyou_crawl()
