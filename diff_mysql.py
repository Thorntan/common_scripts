#code=utf-8

import sys
import db_add
import export

reload(sys)
sys.setdefaultencoding='utf8'

def get_url1():
    sql = "select distinct review_id as id from tp_rest_comment_051102"
    return db_add.QueryBySQL(sql)

def get_url2():
    sql = "select distinct review_id as id from tp_rest_comment_0511"
    return db_add.QueryBySQL(sql)

def insert(args):
    sql = "insert into  tp_rest_comment_051103 select * from  tp_rest_comment_051102 where review_id=%s"
    return db_add.ExecuteSQL(sql,args)

def get_diff():
    a = []
    b = []
    c = []
    d = []
    for i in get_url1():
        mid = i['id']
        a.append( mid )

    for i in get_url2():
        mid = i['id']
        b.append( mid )

    c = list(set(a).difference(set(b)))
    #c = list(set(a).difference(set(b)))
    #c = list(set(a).intersection(set(b)))
    print 'a count: %s' % len(a)
    print 'b count: %s' % len(b)
    print 'c count: %s' % len(c)
    return c

if __name__ in '__main__':
    c = get_diff()
    cc = 0
    for i in c:
        insert(i)
        cc += 1
    print cc,'over'

