import xlrd
import db_add
import db_platform
import db_source
from util.Browser import MechanizeCrawler as MC
import re

def insert(args):
    sql = 'insert ignore into attr_bucket_relation_new(sid,file_name,`use`,status) values(%s,%s,%s,%s)'
    return db_platform.ExecuteSQLs(sql,args)

sql = 'select city_id,id,image_list from restaurant where image_list!=\'\' and city_id in (\'10001\',\'10006\')'

res = db_source.QueryBySQL(sql)

f = open('rest.txt','w')
for i in res:
    sid = i['id']
    cid = i['city_id']
    imgs = i['image_list']
    data_list = []
    for j in imgs.split('|'):
        #print j
        data = ( cid, sid,j,'1','online')
        pic = j.strip() 
        f.write(pic+'\n')
    #    data_list.append(data)
    #print 'insert',insert( data_list ),sid
f.close()


