# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.conf import settings

class DazongdianpingPipeline(object):
    def __init__(self):
        self.client = MongoClient(host=settings['MONGO_HOST'],port=settings['MONGO_PORT'])
        self.db = self.client[settings['MONGO_DB']]
        self.connection = self.db[settings['MONGO_COL']]


    def process_item(self, item, spider):
        try:
            postItem = dict(item)
            self.connection.insert_one(postItem)
            print("成功插入一条数据")
        except Exception as e:
            print(e)
