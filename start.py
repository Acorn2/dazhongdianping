#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/4/3 14:05
software: PyCharm
description: 
'''
from scrapy import cmdline

# cmdline.execute('scrapy crawl hotel_spider'.split(' '))
cmdline.execute('scrapy crawl hotel_spider_correct'.split(' '))