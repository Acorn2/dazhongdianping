#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/6 13:48
software: PyCharm
description: 
'''
import scrapy
from scrapy import Request
from dazongdianping.items import DazongdianpingItem
import requests, re
import time
from pyquery import PyQuery as pq
import bisect


class HotelSpiderCorrect(scrapy.Spider):
    font_size = 14  # 字的大小font-size
    start_y = 23

    name = 'hotel_spider_correct'

    # allowed_domains = ['www.dianping.com']

    start_urls = ['http://www.dianping.com/shanghai/hotel/pn']
    base_url = 'http://www.dianping.com/shop/'

    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 's_ViewType=10; _lxsdk_cuid=16a66be5838c8-0e92fe3848c569-e323069-1fa400-16a66be5838c8; _lxsdk=16a66be5838c8-0e92fe3848c569-e323069-1fa400-16a66be5838c8; _hc.v=a84aaa1c-edb5-f595-f6d2-34f37f1dbaa8.1556501912; dper=23228a5f32fa5a7a6d12419653eedbacf0dcc4f4637e43f3fad26370ab076867c8f6db4e463dc07c6922984bacfc28cf70954720aa539348fca4ccf72f6e6febb0c1b41507587eab35377dcf5355569ffc19cedd44a21f279c33358c2fdb020a; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_4009668476; ctu=be12c2bd5a0922c59d8c17218fe5448046d6a0e0d764296271c0adf8330c5bfb; uamo=17121192617; cityInfo=%7B%22cityId%22%3A1%2C%22cityName%22%3A%22%E4%B8%8A%E6%B5%B7%22%2C%22provinceId%22%3A0%2C%22parentCityId%22%3A0%2C%22cityOrderId%22%3A0%2C%22isActiveCity%22%3Afalse%2C%22cityEnName%22%3A%22shanghai%22%2C%22cityPyName%22%3Anull%2C%22cityAreaCode%22%3Anull%2C%22cityAbbrCode%22%3Anull%2C%22isOverseasCity%22%3Afalse%2C%22isScenery%22%3Afalse%2C%22TuanGouFlag%22%3A0%2C%22cityLevel%22%3A0%2C%22appHotLevel%22%3A0%2C%22gLat%22%3A0%2C%22gLng%22%3A0%2C%22directURL%22%3Anull%2C%22standardEnName%22%3Anull%7D; _lxsdk_s=16a8bfd4843-4ae-9fb-a95%7C%7C368',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
    }

    html_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Host': 'www.dianping.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
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
        for span in re.findall(r'<svgmtsi class="([a-zA-Z0-9]{5,6})"></svgmtsi>', html):
            class_set.add(span)
        for class_name in class_set:
            try:
                html = re.sub('<svgmtsi class="%s"></svgmtsi>' % class_name, font_dict[class_name], html)

            except:
                html = re.sub('<svgmtsi class="%s"></svgmtsi>' % class_name, '', html)

        # class_set2 = set()
        # for span in re.findall(r'<bb class="([a-zA-Z0-9]{5,6})"></bb>', html):
        #     class_set2.add(span)
        # for class_name in class_set2:
        #     try:
        #         html = re.sub('<bb class="%s"></bb>' % class_name, font_dict[class_name], html)
        #
        #     except:
        #         html = re.sub('<bb class="%s"></bb>' % class_name, '', html)

        return html

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

                content = self.parse_url(url, self.headers)

                content_css = self.get_css(content, self.css_headers)
                css_class_dirt = self.get_css_offset(content_css)  # 偏移量字典存储
                svg_url_dict = self.get_svg_url_dict(content_css)  # svg的url dict储存
                print(svg_url_dict)

                font_dict = self.get_font_dict(svg_url_dict=svg_url_dict,css_class_dirt=css_class_dirt)
                html = self.get_conment_page(content, font_dict)
                doc = pq(html)
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

    def parse_url(self, url, headers):
        '''
        解析并返回页面内容
        :param url: 评论页详情地址
        :param headers: 请求头
        :return:
        '''
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        if 200 == response.status_code:
            return response.content.decode()
        else:
            return None

    def get_css(self, html, headers):
        '''
        解析评论页面内容，从中提取css样式文件url，返回css文件源码
        :param html: 评论页面内容
        :param headers: 请求头
        :return: css文件源码
        '''
        # svg_text_css = re.search(r'href="(.*?svgtextcss.*?css)">', html,re.S)
        svg_text_css = re.findall(r'href="(.*?svgtextcss.*?css)">', html, re.M)
        if not svg_text_css:
            return False
        css_url = 'http:' + svg_text_css[0]
        print(css_url)
        content = self.parse_url(css_url, headers)
        return content

    # 获取定义偏移量的css文件后将结果以字典形式存储
    def get_css_offset(self, css_content):
        """
        通过传入页面中任意css获取其对应的偏移量
        :return: {'xxx': ['192', '1550']}
        """
        offset_item = re.findall(r'\.([a-zA-Z0-9]{5,6}).*?background:-(.*?).0px -(.*?).0px', css_content)
        if not offset_item:
            return False
        result = {}
        for item in offset_item:
            css_class = item[0]
            x_offset = int(item[1])
            y_offset = int(item[2])
            result[css_class] = [x_offset, y_offset]
        return result

    # 获取svg url组
    def get_svg_url_dict(self, css_content):
        # items = re.findall(r'span\[class\^="(.*?)"\].*?width: (\d+)px;.*?background-image: url\((.*?)\);', css_content)
        # items = re.findall(r'background-image:.*?\((.*?svg)\)', css_content)
        items = re.findall(r'\[class\^="(.*?)"\].*?width: (\d+)px;.*?background-image: url\((.*?)\);', css_content)

        result = {}
        for code, size, url in items:
            svg_list = [int(size), 'https:' + url]
            result[code] = svg_list
        return result

    def get_font_dict(self, css_class_dirt, svg_url_dict):
        """
            构建class标签元素与位置元素数值对应的映射关系
            获取css样式对应文字的字典
        """
        #根据svg文件不同，匹配不同的svg文件地址，
        #'ukj': [14, 'https://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/04cc0d28efdb7945a60af7aba24ed77b.svg']
        #比如说某个隐藏字段的class为ukj开头，则它的明文对应应该在ukj后的svg文件中匹配
        svg_kind_list = []
        for css_class_name in css_class_dirt.keys():
            svg = svg_url_dict.get(css_class_name[:3], None)
            if not svg:
                continue
            svg_kind_list.append(css_class_name[:3])
        svg_kind_list = list(set(svg_kind_list))
        font_dict = {}

        for svg_kind in svg_kind_list:
            print(svg_kind)
            # 根据偏移量来找到对应的数字
            size = svg_url_dict[svg_kind][0]
            svg_url = svg_url_dict[svg_kind][1]  # svg_url地址
            font_dict_by_offset, y_list = self.get_font_dict_by_offset(svg_url)

            for css_class_name in css_class_dirt.keys():
                # 根据css名称获取偏移量
                x_offset, y_offset = css_class_dirt[css_class_name][0], css_class_dirt[css_class_name][1]
                x = int(x_offset)
                y = int(y_offset)

                x_position = x // size
                y_position = bisect.bisect(y_list, y)#利用bisect查找位置

                try:
                    font_dict[css_class_name] = font_dict_by_offset[y_position]['text'][x_position]
                except:
                    break
        print(font_dict)
        return font_dict

    def get_font_dict_by_offset(self, url):
        """
            获取坐标偏移的文字字典
        """
        res = requests.get(url, headers=self.css_headers)
        html = res.text
        font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html, re.S)

        svg_list = []  # 存放svg页面源码中的内容，按照y值进行分行

        y_list = []  # 存放svg页面源码中每行数据的y值
        for item in font_list:
            y_list.append(int(item[0]))
            svg = {'y_key': int(item[0]), 'text': item[1]}
            svg_list.append(svg)

        return svg_list, y_list
