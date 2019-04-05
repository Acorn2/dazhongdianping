#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/4/3 14:05
software: PyCharm
description: 大众点评酒店爬取用户评论信息
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
        'Cookie': '__mta=256752180.1554272415181.1554282586785.1554346008645.4; cityInfo=%7B%22cityId%22%3A1%2C%22cityName%22%3A%22%E4%B8%8A%E6%B5%B7%22%2C%22provinceId%22%3A0%2C%22parentCityId%22%3A0%2C%22cityOrderId%22%3A0%2C%22isActiveCity%22%3Afalse%2C%22cityEnName%22%3A%22shanghai%22%2C%22cityPyName%22%3Anull%2C%22cityAreaCode%22%3Anull%2C%22cityAbbrCode%22%3Anull%2C%22isOverseasCity%22%3Afalse%2C%22isScenery%22%3Afalse%2C%22TuanGouFlag%22%3A0%2C%22cityLevel%22%3A0%2C%22appHotLevel%22%3A0%2C%22gLat%22%3A0%2C%22gLng%22%3A0%2C%22directURL%22%3Anull%2C%22standardEnName%22%3Anull%7D; _lxsdk_cuid=169e1c3fe45c8-0f754e083bee5c-7a1437-1fa400-169e1c3fe45c8; _lxsdk=169e1c3fe45c8-0f754e083bee5c-7a1437-1fa400-169e1c3fe45c8; _hc.v=8c5f514c-2752-fba0-ff6a-98b837acea0a.1554270912; aburl=1; cy=1; cye=shanghai; _dp.ac.v=8f2de5eb-4671-48a9-a5c5-a385de91ead1; dper=49309ed75899790a8e62c349b50bb374e1aad5d35f033731a577248f0db0f6b6a2a021d7d8a5b9e612c6cb74e948b24ce28814fd96cd8ee773a7cac2553180d1e7a5c110b9b65f7d960dcc7ed7759bf4397084008e19aa9d473980a1d944a937; ua=%E5%92%A9%E5%92%A9%E5%92%A9%E9%85%B1; ctu=41c8e4152f0f10ae8cfafba2c05747080a291cbec5eca405b4ffa5d152eaa12a; selectLevel=%7B%22level1%22%3A%221%22%2C%22level2%22%3A%221%22%7D; ll=7fd06e815b796be3df069dec7836c3df; s_ViewType=10; _lxsdk_s=169eb0c944d-26a-3fe-237%7C%7C745',
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
        background_image_link2 = 'http:' + background_image_link[2]
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

                html = self.get_conment_page(html, font_dict2)
                doc = pq(html)

                item['hotel_address'] = doc('.address-info').text().replace('\xa0', '')  # 存在隐藏字段，需要转换
                assert item
                results = doc('.reviews-items > ul > li ').items()
                for com in results:
                    it = DazongdianpingItem()
                    it = item
                    it['comment_user'] = com.find('.dper-info > a').text()
                    it['comment_desc'] = com.find('.Hide').text().replace('\t', '').replace(
                        '\n', '').replace('\xa0', '')

                    desc_list = com.find('.Hide').text().replace('\t', '').replace(
                        '\n', '')

                    pic_list = []
                    for p in com.find('.review-pictures > ul > li > a').items():
                        pic_list.append('http://www.dianping.com' + p.attr('href'))
                    it['comment_pics'] = pic_list
                    # print(it)
                    yield it
            # n += 1
            # if n == 1:
            #     break



