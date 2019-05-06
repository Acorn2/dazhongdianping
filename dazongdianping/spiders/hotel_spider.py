#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/4/3 14:05
software: PyCharm
description: 大众点评酒店爬取用户评论信息
https://blog.csdn.net/sinat_32651363/article/details/85123876
'''

import scrapy
from scrapy import Request
from dazongdianping.items import DazongdianpingItem
import requests, re
import time
from pyquery import PyQuery as pq


class HotelSpider(scrapy.Spider):
    font_size = 14  # 字的大小font-size
    start_y = 23

    name = 'hotel_spider'

    # allowed_domains = ['www.dianping.com']

    start_urls = ['http://www.dianping.com/shanghai/hotel/pn']
    base_url = 'http://www.dianping.com/shop/'

    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 's_ViewType=10; _lxsdk_cuid=16a66be5838c8-0e92fe3848c569-e323069-1fa400-16a66be5838c8; _lxsdk=16a66be5838c8-0e92fe3848c569-e323069-1fa400-16a66be5838c8; _hc.v=a84aaa1c-edb5-f595-f6d2-34f37f1dbaa8.1556501912; dper=23228a5f32fa5a7a6d12419653eedbacf0dcc4f4637e43f3fad26370ab076867c8f6db4e463dc07c6922984bacfc28cf70954720aa539348fca4ccf72f6e6febb0c1b41507587eab35377dcf5355569ffc19cedd44a21f279c33358c2fdb020a; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_4009668476; ctu=be12c2bd5a0922c59d8c17218fe5448046d6a0e0d764296271c0adf8330c5bfb; uamo=17121192617; _lxsdk_s=16a8bced4f4-63c-e21-c19%7C%7C1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
    }

    css_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
    }

    def start_requests(self):
        for i in range(1, 2):
            # http://www.dianping.com/shanghai/hotel/pnp3
            url = self.start_urls[0] + str(i)
            yield Request(url, headers=self.headers, callback=self.parse)

    def get_conment_page(self, html, font_dict):
        """
            请求评论页，并将<span></span>样式和<bb></bb>样式替换成文字
            进行class属性元素与隐藏文字的替换
        """
        class_set = set()
        for span in re.findall(r'<span class="([a-zA-Z0-9]{5,6})"></span>', html):
            class_set.add(span)
        for class_name in class_set:
            try:
                html = re.sub('<span class="%s"></span>' % class_name, font_dict[class_name], html)

            except:
                html = re.sub('<span class="%s"></span>' % class_name, '', html)

        class_set2 = set()
        for span in re.findall(r'<bb class="([a-zA-Z0-9]{5,6})"></bb>', html):
            class_set2.add(span)
        for class_name in class_set2:
            try:
                html = re.sub('<bb class="%s"></bb>' % class_name, font_dict[class_name], html)

            except:
                html = re.sub('<span class="%s"></span>' % class_name, '', html)

        return html

    def get_css_link(self, url):
        """
            请求评论首页，获取css样式文件和html文件
        """
        try:
            res = requests.get(url, headers=self.headers)
            html = res.text
            css_link = re.search(r'<link re.*?css.*?href="(.*?svgtextcss.*?)">', html)
            css_link = 'http:' + css_link[1]
            assert css_link
            return html, css_link
        except:
            None

    def get_css_svg(self, url):
        '''
        评论区内容span块里的隐藏内容，地址bb块里的隐藏内容，对应着不同的svg文件
        :param url:
        :return:
        '''
        res = requests.get(url, headers=self.css_headers)
        html = res.text
        background_image_link = re.findall(r'background-image:.*?\((.*?svg)\)', html)
        assert background_image_link
        # <bb>样式表
        background_image_link1 = 'http:' + background_image_link[1]
        # <span>样式表
        background_image_link2 = 'http:' + background_image_link[0]
        return html, background_image_link1, background_image_link2

    def get_font_dict(self, html, background_image_link):
        """
            构建class标签元素与位置元素数值对应的映射关系
            获取css样式对应文字的字典
        """
        # res = requests.get(url, headers=self.css_headers)
        # html = res.text
        # background_image_link = re.findall(r'background-image:.*?\((.*?svg)\)', html)
        # assert background_image_link
        # background_image_link = 'http:' + background_image_link[2]
        # print('----------' * 40)
        # print(background_image_link)
        # print('---------------' * 40)
        html = re.sub(r'span.*?\}', '', html)
        group_offset_list = re.findall(r'\.([a-zA-Z0-9]{5,6}).*?round:(.*?)px (.*?)px;', html)
        font_dict_by_offset = self.get_font_dict_by_offset(background_image_link)
        font_dict = {}
        for class_name, x_offset, y_offset in group_offset_list:
            x_offset = x_offset.replace('.0', '')
            y_offset = y_offset.replace('.0', '')

            try:
                font_dict[class_name] = font_dict_by_offset[int(y_offset)][int(x_offset)]

            except:
                font_dict[class_name] = ''
        print(font_dict)
        return font_dict

    def get_font_dict_by_offset(self, url):
        """
            获取坐标偏移的文字字典, 会有最少两种形式的svg文件（目前只遇到两种）
        """
        res = requests.get(url, headers=self.css_headers)
        html = res.text
        font_dict = {}
        y_list = re.findall(r'd="M0 (\d+?) ', html)
        if y_list:
            font_list = re.findall(r'<textPath .*?>(.*?)<', html)
            for i, string in enumerate(font_list):
                y_offset = self.start_y - int(y_list[i])

                sub_font_dict = {}
                for j, font in enumerate(string):
                    x_offset = -j * self.font_size
                    sub_font_dict[x_offset] = font

                font_dict[y_offset] = sub_font_dict
        else:
            font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html)

            for y, string in font_list:
                y_offset = self.start_y - int(y)
                sub_font_dict = {}
                for j, font in enumerate(string):
                    x_offset = -j * self.font_size
                    sub_font_dict[x_offset] = font

                font_dict[y_offset] = sub_font_dict
            # print(font_dict)
        return font_dict

    def parse(self, response):
        sel = scrapy.Selector(response)

        hotel = sel.xpath('//li[@class="hotel-block"]')
        n = 0
        for h in hotel:
            item = DazongdianpingItem()
            item['hotel_id'] = sel.xpath('//li[@class="hotel-block"]/@data-poi').extract()[n]
            item['hotel_name'] = h.xpath('.//h2[@class="hotel-name"]/a[@class="hotel-name-link"]/text()').extract()[
                0].replace('\t', '').replace(
                '\n', '')
            item['hotel_place'] = h.xpath('.//p[@class="place"]/a/text()').extract()[0] + \
                                  h.xpath('.//p[@class="place"]/span/text()').extract()[0]
            item['comment_num'] = h.xpath('.//a[@class="comments"]/text()').extract()[0].replace('(', '').replace(
                ')', '')

            # 每个酒店抓取一定页数的评论
            for i in range(1, 2):
                url = self.base_url + item['hotel_id'] + '/review_all/p' + str(i)

                html, css_link = self.get_css_link(url)
                print(css_link)
                css_content, link1, link2 = self.get_css_svg(css_link)
                print(link1)
                print(link2)
                # 地址隐藏区内容
                # font_dict1 = self.get_font_dict1(css_content,link1)
                # 评论隐藏区内容
                font_dict2 = self.get_font_dict(css_content, link2)

                # 实际测试过程中，发现<bb>和<span>对应的隐藏表有相同之处，因此选择使用更大的映照表

                time.sleep(2)

                # html = self.get_conment_page(html, font_dict2)
                # doc = pq(html)
                #
                # item['hotel_address'] = doc('.address-info').text().replace('\xa0', '')  # 存在隐藏字段，需要转换
                # assert item
                # results = doc('.reviews-items > ul > li ').items()
                # for com in results:
                #     it = DazongdianpingItem()
                #     it = item
                #     it['comment_user'] = com.find('.dper-info > a').text()
                #     it['comment_desc'] = com.find('.Hide').text().replace('\t', '').replace(
                #         '\n', '').replace('\xa0', '')
                #
                #     desc_list = com.find('.Hide').text().replace('\t', '').replace(
                #         '\n', '')
                #
                #     pic_list = []
                #     for p in com.find('.review-pictures > ul > li > a').items():
                #         pic_list.append('http://www.dianping.com' + p.attr('href'))
                #     it['comment_pics'] = pic_list
                #     print(it)
                    # yield it
            n += 1
            if n == 1:
                break



