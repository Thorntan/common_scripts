#coding=utf-8
import sys
from util.Browser import MechanizeCrawler as MC
import json
import re
import db_add
import time
reload(sys)
sys.setdefaultencoding('utf-8')

def insert(args):
    sql = "insert ignore into mafengwo_city values(%s,%s,%s,%s,%s)"
    return db_add.ExecuteSQL(sql,args)

def get_task():
    #sql = "select * from mafengwo_country where id='11656'"
    sql = "select * from mafengwo_country order by id"
    return db_add.QueryBySQL(sql)

def crawl(url):
    mc = MC()
    page = mc.req('get',url,html_flag=True)
    #open('test','w').write(page)
    return page

def parse(cid):
    country_url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid=%s&iType=3&iPage=1' % cid
    page = crawl(country_url)
    d = json.loads(page)

    for c in d['list']:
        sid = c['id']
        name = c['name'].encode('utf-8')
        map_info = str(c['lng'])+','+str(c['lat'])
        print sid,name,map_info
        url = "http://www.mafengwo.cn/travel-scenic-spot/mafengwo/%s.html" % sid
        print 'insert',insert((sid,name,map_info,cid,url))

if __name__ in '__main__':
    for i in get_task():
        print i['id']
        parse(i['id'])
        break
        time.sleep(2)
