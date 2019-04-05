# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DazongdianpingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    hotel_name = scrapy.Field()#酒店名称
    hotel_id = scrapy.Field()#酒店id
    hotel_place = scrapy.Field()#酒店位置
    hotel_address = scrapy.Field()#酒店详细地址
    hotel_score = scrapy.Field()#酒店评分/5分制
    comment_num = scrapy.Field()#评论数
    comment_user = scrapy.Field()#写评论的用户名
    comment_desc = scrapy.Field()#评论内容
    comment_pics = scrapy.Field()#评论时上传的图片
