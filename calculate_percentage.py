#coding=utf8
"""
    @desc: 计算重要字段有有效值的百分比,并将结果写入excel表中
"""

import xlwt
import db_add
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# --- 导出的excel文件 ------
# 文件名
FILE_NAME = 'test.xlsx'
# 工作表名
SHEET_NAME = 'test'


# ----------- 需要修改的变量  -----------------------


# ***************** 数据库表名 ******************
DB_TABLE = 'tp_shop_comment_0526'

# **************** 需要统计的字段 ************
# 餐厅
#COLUMN = ['miaoji_id','city_id','id','source','name','name_en','grade','price','telphone','map_info','address','open_time','cuisines','res_url','review_num','menu','tags_comm','image_urls']
# 购物
#COLUMN = ['miaoji_id','city_id','name','name_en','map_info','address','grade','commentcounts','tagid','url','phone','opentime','price','imgurl','introduction']
# 景点
#COLUMN = ['miaoji_id','city_id','name','name_en','map_info','address','star','grade','ranking','beentocounts','commentcounts','cateid','phone','site','introduction']
# 评论
COLUMN = ['miaoji_id','source','source_id','review_id','review_title','review_text','review_link','comment_time','comment_rating','user_id','user_name','user_rating','user_link','likes','review_from']

# SQL语句
TOTAL_SQL = 'select count(*) from %s ' % DB_TABLE

# ------------- END --------------------------


def query_db():
    return db_add.QueryBySQL(QUERY_SQL)

def get_total():
    result = db_add.QueryBySQL(TOTAL_SQL)
    return int(result[0]['count(*)'])

def get_col_count(col):
    args = (col,col,col,col)
    sql = "select count(*) from "+DB_TABLE+" where %s is not null and %s !=\'NULL\' and %s !=\'\' and %s !=\'-1\'" % args
    result = db_add.QueryBySQL(sql)
    return int(result[0]['count(*)'])

def cal(col,total):
    col = float(col)
    total = float(total)
    return float(col/total)

if __name__ in '__main__':
    total = get_total()
    print 'total_num:',total

    txt = open('test.txt','a')
    f = xlwt.Workbook()
    sheet = f.add_sheet(SHEET_NAME,cell_overwrite_ok=True)

    col = 0
    for col_name in COLUMN:
        col_count = get_col_count(col_name)
        percent = cal(col_count,total)
        per = "%.2f%%" % (percent*100)
        print col_name,'\t','\t',per
        sheet.write(0,col,col_name)
        sheet.write(2,col,str(per))
        sheet.write(3,col,col_count)
        txt.write(col_name+'\t'+str(per)+'\t'+str(col_count)+'\n')
        col += 1

    f.save(FILE_NAME)
    txt.close()

    # 写一个单元格,注意行号和列号都是从0开始
    #sheet.write(行号,列号,'内容')
