# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class NewsPipeline(object):
    def __init__(self):
        # 建立数据库连接
        self.Connection = pymysql.Connect(host='127.0.0.1', port=3306, user='root', password='mysql5725', db='news',
                                          charset='utf8')
        # 创建操作游标
        self.cursor = self.Connection.cursor()

    def process_item(self, item, spider):
        # 定义sql语句
        sql = "INSERT INTO news.news_info(title, text, date, source, href) VALUES(" + " \" " +item["title"]+ " \" " + "," + " \" "+ item["text"] + " \" "+ "," + " \" "+ item["date"]+ " \" " + "," + " \" "+ item["source"]+ " \" " + "," + " \" "+ item["href"]+ " \" " + ")"

        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 保存修改
            self.Connection.commit()
        except Exception as err:
            # 如果发生错误,立即回滚
            self.Connection.rollback()
            # 并打印出错误
            print(err)
        # print("信息写入数据库成功！")
        return item

    def __del__(self):
        # 关闭操作游标
        self.cursor.close()
        # 关闭数据库连接
        self.Connection.close()
