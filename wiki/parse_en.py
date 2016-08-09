#coding=utf-8
'''
    @author:    yanlihua
    @date:      2016-01-05
    E@desc:      wiki
    @update:    2016-01-05
'''
import sys
from lxml import html as HTML
from util.Browser2 import MechanizeCrawler as MC
#from Browser2 import MechanizeCrawler as MC
import traceback
import re
import json
import db_add
import urllib
import wikipedia
import time

reload(sys)
sys.setdefaultencoding('utf-8')

def get_task():
    sql = "select * from wiki_0427 where flag ='NULL' and summary is null"
    return db_add.QueryBySQL(sql)

def insert_db(args):
    #sql = 'update google set wiki_en_url=%s,summary_en=%s,wiki_en_title=%s,wiki_en_img=%s where miaoji_id = %s'
    sql = 'update wiki_0427 set wiki_url=%s,wiki_title=%s,summary=%s where miaoji_id = %s'
    #return db_add.ExecuteSQL(sql,args)


if __name__ in '__main__':

    count = 0
    for i in get_task():
        print '--------- count: %s --------' % count
        mid = i['miaoji_id']
        #name = i['name'].encode('utf-8')
        name = i['name_en'].encode('utf-8')
        #name = 'Jewish Museum, Berlin'
        city_id = i['city_id'].encode('utf-8')
        #url = i['wiki_url']
        print 'task:',mid,name
        try:
            #result = crawl( name,mid )    
            wikipedia.set_lang('en')
            wk = wikipedia.page(name)
            url = wk.url.encode('utf-8')
            title = wk.title.encode('utf-8')
            summary_en = wk.summary.encode('utf-8').strip()
            ##@坚哥要求，wiki英文简介以500个单词为限，超过500的，取前三段，低于500的取全部。
            if len(summary_en.split(' '))>500:
                summary_en = '\n'.join(summary_en.split('\n')[:3])
            try:
                img = wk.images
                img = '|'.join(img)
            except:
                img = 'NULL'
            print title,url
            print summary_en
        except Exception,e:
            print 'crawl error',mid
            print str(e)
            url,summary_en,title,img = 'NULL','NULL','NULL','NULL'
        #data = ( url,summary_en,title,img, mid )
        data = ( url,title,summary, mid )
        print 'update',insert_db( data ),mid

        count += 1
        break
        time.sleep(1)
    print 'over',count
