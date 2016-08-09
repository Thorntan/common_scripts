import xlrd
import db_add
import db_source
from util.Browser import MechanizeCrawler as MC
import re
'''
def insert(args):
    sql = 'insert into v2city values(%s,%s,%s,%s)'
    return db_add.ExecuteSQLs(sql,args)
'''

def get_attr():
    sql = 'select id,name,name_en,map_info,city_id,city from attraction where map_info!=\'\' and map_info!=\'NULL\''
    return db_source.QueryBySQL(sql)

def insert(args):
    sql = 'insert ignore attr_task values(%s,%s,%s,%s,%s,%s,%s)'
    return db_add.ExecuteSQL(sql,args)

count = 0
for a in get_attr():
    print 'count:',count
    mid = a['id'].encode('utf-8')
    name = a['name'].encode('utf-8')
    name_en = a['name_en'].encode('utf-8')
    map_info = a['map_info'].encode('utf-8')
    city_id = a['city_id'].encode('utf-8')
    city_name = a['city'].encode('utf-8')
    data = (mid, name, name_en, map_info, city_id, city_name,'NULL')
    print data
    print 'insert',insert( data )
    count += 1
