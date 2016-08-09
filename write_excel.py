#coding=utf8
import xlwt
import db_add
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 文件名
FILE_NAME = 'test.xlsx'
# 工作表名
SHEET_NAME = 'test'

# 字段名
# SQL语句

# rest
#COLUMN = ['id','source','name','grade','price','telphone','map_info','address','open_time','cuisines','res_url','service','payment','review_num','menu','tags_comm']
#QUERY_SQL = 'select id,source,name,grade,price,telphone,map_info,address,open_time,cuisines,res_url,service,payment,review_num,menu,tags_comm from tp_rest_basic_0324 order by rand() limit 50'

# comment
#COLUMN = ['source','source_id','review_id','review_title','review_text','review_link','comment_time','comment_rating','user_name','user_rating','user_link','likes','review_from','miaoji_id']
#QUERY_SQL = 'select source,source_id,review_id,review_title,review_text,review_link,comment_time,comment_rating,user_name,user_rating,user_link,likes,review_from,miaoji_id from tp_attr_comment_0419 order by rand() limit 50'

#COLUMN = ['source','id','source_city_name','city_id','name','name_en','url']
#QUERY_SQL = 'select source,id,source_city_name,city_id,name,name_en,url from qyer_japan'

# shop
#COLUMN = ['name','name_en','map_info','address','star','grade','ranking','beentocounts','commentcounts','cateid','phone','site','url','imgurl','introduction']
#QUERY_SQL = 'select name,name_en,map_info,address,star,grade,ranking,beentocounts,commentcounts,cateid,phone,site,url,imgurl,introduction from tp_shop_basic_0324 order by rand() limit 50'

#attr
#COLUMN = ['name','name_en','map_info','address','star','grade','ranking','beentocounts','commentcounts','cateid','phone','site','url','introduction']
#QUERY_SQL = 'select name,name_en,map_info,address,star,grade,ranking,beentocounts,commentcounts,cateid,phone,site,url,introduction from qyer_japan order by rand() limit 50'
# qyer_city
#COLUMN = ['source_country_id','source_country_name','source_country_name_en','source_city_id','source_city_name','source_city_name_en','city_id','city_url']
#QUERY_SQL = 'select source_country_id,source_country_name,source_country_name_en, source_city_id,source_city_name,source_city_name_en,city_id,city_url from qyer_city order by source_country_id'

#COLUMN = ['id','name','name_en','map_info','city_type','country','country_id','continent','status']
#QUERY_SQL = "select id,name,name_en,map_info,city_type,country,country_id,continent,status from city"
#google
#COLUMN = ['miaoji_id','name','address','grade','rating_num','website']
#QUERY_SQL = 'select * from google_0331 order by rand() limit 100'

#wiki
#COLUMN = ['miaoji_id','name_zh','wiki_url','wiki_title','summary']
#QUERY_SQL = 'select * from wiki_0429 order by miaoji_id limit 2000,600 '
#COLUMN = ['route','url','days','price','sold_num','origin_route']
COLUMN = ['city','price','days','city_day','url','title']
QUERY_SQL = 'select * from ctrip where flag=\'1\''
def query_db():
    return db_add.QueryBySQL(QUERY_SQL)

if __name__ in '__main__':

    results = query_db()
    row_total = len(results)
    
    # 新建一个excel表格 
    f = xlwt.Workbook()
    
    # 新建一个工作表
    sheet = f.add_sheet(SHEET_NAME,cell_overwrite_ok=True)
    
    # 第0行， 表头写字段名
    for col in range(0,len(COLUMN)):
        sheet.write(0,col,COLUMN[col])
    
    # 从第0列第1行开始，写单元格
    for row in range(1,row_total+1):
        # 逐行读取查询结果，从0开始
        result = results[row-1]
        # 把每个字段的值写进list，方便用索引读取结果
        data = []
        for num in range(0,len(COLUMN)):
            data.append( result[COLUMN[num].encode('utf-8')] )

        for col in range(0,len(COLUMN)):
            print '正在写入单元格:',row,col
            sheet.write(row,col,data[col])
    
    # 保存到excel表格
    f.save(FILE_NAME)


    # 写一个单元格,注意行号和列号都是从0开始
    #sheet.write(行号,列号,'内容')
