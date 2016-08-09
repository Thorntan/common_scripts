#coding=utf-8
'''
    @author:    yanlihua
    @date:      2016-01-05
    @desc:      wiki
    @update:    2016-01-05
'''
import sys
from lxml import html as HTML
from util.Browser2 import MechanizeCrawler as MC
import traceback
import re
#import wikiapi
#import wikipedia
import json
import db_add
import urllib

reload(sys)
sys.setdefaultencoding('utf-8')

def get_task():
    sql = 'select * from wiki_en where content is null and name!=\'NULL\''
    return db_add.QueryBySQL(sql)

def insert_db(args):
    sql = 'update wiki_en set content = %s  where miaoji_id = %s'
    #sql = 'replace into wiki_cn(miaoji_id,name,name_en,map_info,city_id,url,content,new_name_en) values(%s,%s,%s,%s,%s,%s,%s,%s)'
    return db_add.ExecuteSQL(sql,args)

def get_page( url ):
    #url = 'https://zh.wikipedia.org/w/api.php?action=query&titles=%E5%8D%A2%E6%B5%AE%E5%AE%AB&prop=revisions&converttitles=&rvprop=content&format=json'
    # 中文wiki需要翻墙,且关键字必须是中文
    #url = 'https://zh.wikipedia.org/w/api.php?action=query&titles=%s&prop=revisions&converttitles=&rvprop=content&format=json' % key
    mc = MC()
    #mc.set_debug(True)
    #p = get_proxy(forbid_regions=['CN'])
    #mc.set_proxy(p)
    #print p
    page = mc.req('get',url,html_flag=True)
    open('test.html','w').write(page[0])
    return page[0]

def crawl(task):
    content = ''
    new_name = 'NULL'
    url = 'https://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=revisions&converttitles=&rvprop=content&format=json' % task.replace(' ','%20')
    #url = 'http://en.wikipedia.org/wiki/Neue_Kirche,_Berlin'
    #url = 'http://en.wikipedia.org/wiki/%s' % task.replace(' ','_').replace('&','and')
    #url = 'https://zh.wikipedia.org/w/api.php?action=query&titles=%s&prop=revisions&converttitles=&rvprop=content&format=json' % task.replace(' ','%20')
    print url
    page = get_page( url )
    open('test.html','w').write(page)

    is_no_info = len(re.compile(r'"(missing)":""}').findall(page))
    if is_no_info:
        print 'no info !!!'
        return content
    data = json.loads(page)
    pageid = data['query']['pages'].keys()[0]
    content = data['query']['pages'][pageid]['revisions'][0]['*']
    if content.find('#REDIRECT [[') > -1:
        print 'no the right name!! try another...'
        print task
        task = content.split('[[')[1].split(']]')[0]
        #key = re.compile(r'#REDIRECT ([[.*]])').findall( content )[0].encode('utf-8') 
        url = 'https://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=revisions&converttitles=&rvprop=content&format=json' % task.replace(' ','%20')
        print url
        page = get_page( url )
        is_no_info = len(re.compile(r'"(missing)":""}').findall(page))
        if is_no_info:
            print 'no info !!!'
            return content
        page = get_page( url ) 
        data = json.loads(page)
        pageid = data['query']['pages'].keys()[0]
        content = data['query']['pages'][pageid]['revisions'][0]['*']
        new_name = task

    return content,url,new_name


if __name__ in '__main__':

    #task = 'Louvre'
    #print wikipedia.search('New York')
    #print wikipedia.summary("Wikipedia")
    #url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670,151.1957&radius=500&types=food&name=cruise&key=AIzaSyA4zl35walR40QzpxN7VbLzyeXkTUJYV_c'
    #url = 'https://en.wikipedia.org/w/api.php?action=query&titles=Louvre&prop=revisions&converttitles=&rvprop=content&format=json'
    #content = crawl( task )
    #print len(content)

    url = 'http://10.10.177.197:8086/proxy?user=overseas&passwd=overseasproxy.mioji'
    p = get_page(url)
    mc = MC()
    mc.set_debug(True)
    mc.set_proxy(p)
    print 'proxy:',p
    url = 'https://zh.wikipedia.org/wiki/Wiki%E6%A0%87%E8%AE%B0%E8%AF%AD%E8%A8%80'
    url = 'http://www.google.com/'
    url = 'https://maps.googleapis.com/maps/api/place/details/json?location=2.337655%2C48.860590&query=u%27La%20Tour%20Eiffel%27&radius=500&key=AIzaSyBu6_rUcZp5SrnNvqUEJdHPvloVqBiACDw'
    url = 'http://www.shutterstock.com/cat.mhtml?autocomplete_id=&language=en&lang=en&search_source=&safesearch=1&version=llv1&searchterm=Louvre&media_type=photos'
    page = mc.req('get',url,html_flag=True)
    open('test2.html','w').write(page[0])
    count = 0
    '''
    for i in get_task():
        print '--------- count: %s --------' % count
        sid = i['miaoji_id']
        name_en = i['name'].encode('utf-8')
        print 'task:',sid,name_en
        try:
            result = crawl( name_en )    
        except Exception,e:
            print 'crawl error',sid
            print str(e)
            result = []
        if len(result) < 2:
            url = 'NULL'
            content = 'NULL'
            new_name = 'NULL'
        else:
            print 'success',sid
            url = result[1]
            content = result[0]
            new_name = result[2]
        #data = (sid,name,name_en,map_info,city_id,url,content,new_name)
        data = ( content,sid )
        #print 'update',insert_db( data )
        count += 1
        '''
