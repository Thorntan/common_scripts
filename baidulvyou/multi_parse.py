#coding:utf-8
import threading
import random
import Queue
from time import sleep,ctime
import sys
import baidu_parse
import db_add

def get_url():
    sql = 'select url from baidu where map_info is null'
    result = db_add.QueryBySQL(sql)
    return result

#继承一个Thread类，在run方法中进行需要重复的单个函数操作
class MyThread(threading.Thread):
    def __init__(self,queue,lock,num):
        #传递一个队列queue和线程锁，并行数
        threading.Thread.__init__(self)
        self.queue=queue
        self.lock=lock
        self.num=num
    def run(self):
        with self.num:#同时并行指定的线程数量，执行完毕一个则死掉一个线程
            #以下为需要重复的单次函数操作
            url = self.queue.get()#等待队列进入

            #lock.acquire()#锁住线程，防止同时输出造成混乱
            print '----------%s------------' % url
            print '%s Start a new thread：%s' % (ctime(),self.name)
            ##print '队列剩余：',queue.qsize()
            #lock.release()

            try:
                baidu_parse.BaiduParser().crawl(url)
            except Exception,e:
                print str(e)

            #sleep(1)#执行单次操作，这里sleep模拟执行过程

            self.queue.task_done()#发出此队列完成信号


if __name__ == '__main__':

    #while (len(get_url()) != 0):

    for a in range(20000,1000,-1000):
        threads = []
        queue = Queue.Queue()
        lock = threading.Lock()
        num = threading.Semaphore(4)#设置同时执行的线程数为3，其他等待执行
    
        #启动所有线程
        for i in get_url()[a-1000:a]:#总共需要执行的次数
            url = i['url'].encode('utf-8') 
            #queue.put( url )
            t = MyThread( queue, lock, num )
            t.start()
            threads.append(t)
            queue.put( url )
            #queue.put( url )
            #吧队列传入线程，是run结束等待开始执行

        #等待线程执行完毕
        for t in threads:
            t.join()

        queue.join()#等待队列执行完毕才继续执行，否则下面语句会在线程未接受就开始执行

    print 'all over'
