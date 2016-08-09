import xlrd
import db_add
from util.Browser import MechanizeCrawler as MC
import re
import math
from common.common import get_proxy
import json

def get_task():
    #sql = 'select * from pan_task where img_url is null'
    sql = 'select * from pan_task where pic_flag is null'
    return db_add.QueryBySQL(sql)

def insert_db(args):
    #sql = 'update pan_task set url=%s,img_url=%s,flag=2 where miaoji_id = %s'
    #sql = 'update pan set url=%s,img_url=%s,flag=1 where miaoji_id = %s'
    sql = 'insert ignore into pan( miaoji_id,name,name_en,map_info, photo_id,photo_title,url,file_url, longitude,latitude,width,height, upload_date,owner_id,owner_name,owner_url ) values(%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s)'
    return db_add.ExecuteSQLs(sql,args)

def update(args):
    sql = 'update pan_task set pic_flag = %s where miaoji_id = %s'
    return db_add.ExecuteSQL(sql,args)

def parse(content,miaoji_id,name,name_en,map_info):
    dic = json.loads(content)
    if int(dic['count']) !=0 and len(dic['photos']) !=0:
        lat = dic['map_location']['lat']
        lon = dic['map_location']['lon']
        print 'panoramio map_info:',lon,lat
        data_list = []
        count = 0
        for i in dic['photos']:
            photo_id = i['photo_id']
            photo_title  = i['photo_title']
            url  = i['photo_url']
            file_url  = i['photo_file_url']
            longitude  = i['longitude']
            latitude  = i['latitude']
            width  = i['width']
            height  = i['height']
            upload_date  = i['upload_date']
            owner_id  = i['owner_id']
            owner_name  = i['owner_name']
            owner_url  = i['owner_url']
            if int(width) > 499:
                count += 1
            data = ( miaoji_id,name,name_en,map_info, photo_id,photo_title,url,file_url, longitude,latitude,width,height, upload_date,owner_id,owner_name,owner_url )
            data_list.append( data )
        print len(data_list)
        print 'width > 500:',count
        #r = insert_db( data_list )
        #print 'insert ok'
        if r > 0:
            update( ('1',miaoji_id) )
    else:
        print 'no photo !!!',miaoji_id
        update( ('0',miaoji_id) )

if __name__ in '__main__':
   
    mc = MC()
    mc.set_debug(True)
    #p = get_proxy(forbid_regions=['CN']) 
    p = '189.85.20.14:8080'
    #p = '27.123.2.10:8080'
    #p = '1.171.148.235:8088'
    #p = '186.95.3.207:8080'
    #p = '124.127.92.150:6823'
    #p = '207.5.112.114:8080'
    #p = '27.51.132.185:8088'
    #p = '190.36.95.106:8080'
    #p = '190.207.187.35:8080'
    #p = '186.95.60.4:8080'
    #furl = 'http://10.10.177.197:8087/proxy?user=platform&passwd=platformmioji&source=platform'
    #furl = 'http://120.132.92.44:8087/proxy?user=platform&passwd=platformmioji&source=platform'
    #p = mc.req('get',furl,html_flag=True)
    #p = '190.198.115.243:8080'
    mc.set_proxy( p )
    print 'proxy: %s' % p
    count = 0
    for i in get_task():
        print '-------------- count:%s ------------------' % count
        miaoji_id = i['miaoji_id']
        name = i['name'].encode('utf-8')
        name_en = i['name_en'].encode('utf-8')
        map_info = i['map_info']
        print miaoji_id,name,name_en
        print 'origin map_info:',map_info
        x = float( map_info.split(',')[0] )
        y = float( map_info.split(',')[1] )

        minx = round( x-0.0007, 4 )
        miny = round( y-0.0007, 4 )
        maxx = round( x+0.0007, 4 )
        maxy = round( y+0.0007, 4 )
        #print minx,miny,maxx,maxy
        # &size=origin
        url = 'http://www.panoramio.com/map/get_panoramas.php?order=popularity&set=public&from=0&to=100&minx=%s&miny=%s&maxx=%s&maxy=%s&mapfilter=true' % (minx,miny,maxx,maxy)
        page = mc.req('get',url,html_flag=True)
        while len(page) < 100:
            p = get_proxy(forbid_regions=['CN']) 
            mc.set_proxy( p )
            print 'proxy: %s' % p
            page = mc.req('get',url,html_flag=True)
        #open('pan.html','w').write(page)
        #page = open('pan.html','r').read()
        print 'ok proxy: %s' % p
        dic = json.loads(page)
        try:
            parse( page,miaoji_id,name,name_en,map_info ) 
        except Exception,e:
            print 'error:',str(e)
        count += 1
