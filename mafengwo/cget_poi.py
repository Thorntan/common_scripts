#coding=utf-8
import sys
from util.Browser import MechanizeCrawler as MC
import json
import re
import db_add
import time
reload(sys)
sys.setdefaultencoding('utf-8')

source = 'mafengwo'

def insert(args):
    sql = "insert ignore into mafengwo_0618(id,name,name_en,map_info,source,source_city_id,url) values(%s,%s,%s,%s,%s,%s,%s)"
    return db_add.ExecuteSQL(sql,args)

def get_task():
    sql = "select * from guba_task where url3 !='NULL' order by id"
    return db_add.QueryBySQL(sql)

def crawl(url):
    mc = MC()
    content = mc.req('get',url,html_flag=True)
    return content

def parser(cid):
    global source
    # 抓取第一页及其翻页数
    url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid=%s&iType=3&iPage=1' % cid
    print 'url:',url
    data = json.loads(crawl(url))
    total = int(data['total'])
    print 'total:',total
    get_poi(data,cid)
    if total > 30:
        paging(cid,total)
    time.sleep(2)

def paging(cid,total):
    global source
    # 翻页规律，每页30条数据，但是每3页的数据都是一样的
    for i in range(4,int(total/10)+3,3):
        url = ''
        try:
            url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid=%s&iType=3&iPage=%s' % (cid,i)
            print 'url:',url
            data = json.loads(crawl(url))
            get_poi(data,cid)
            time.sleep(2)
        except:
            pass

def has_chinese(contents,encoding='utf-8'):
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    if not isinstance(contents,unicode):
        u_contents = unicode(contents,encoding=encoding)
    results = zh_pattern.findall(u_contents)
    if len(results) > 0:
        return True
    else:
        return False

def get_poi(d,cid):
    for c in d['list']:
        sid = c['id']
        name = c['name'].encode('utf-8')
        if name.find('(')>-1:
            name_cn = name.split('(')[0].strip()
            name_en = name.split('(')[1].replace(')','').strip()
            if has_chinese(name_en):
                name_en = ''
        elif name.find('（')>-1:
            name_cn = name.split('（')[0].strip()
            name_en = name.split('（')[1].replace('）','').strip()
            if has_chinese(name_en):
                name_en = ''
        else:
            name_cn = name
            if has_chinese(name):
                name_en = ''
            else:
                name_en = name
        map_info = str(c['lng'])+','+str(c['lat'])
        url = "http://www.mafengwo.cn/poi/%s.html" % sid
        print sid,name_cn,name_en,map_info
        print 'insert',insert((sid,name_cn,name_en,map_info,source,cid,url))

if __name__ in '__main__':

    count = 0
    for task in get_task():
        print 'count:',count
        cid = re.compile(r'(\d+)').findall(task['url3'])[0]
        parser(cid)
        time.sleep(2)

    print count,'over'
