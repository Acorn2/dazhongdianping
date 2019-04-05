#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/4/3 15:37
software: PyCharm
description:大众点评中的评论部分是隐藏字段，需要转换成汉字显示
参考网址：https://blog.csdn.net/weixin_42512684/article/details/86775357
'''

import datetime
import random
import time
import re
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import pymongo

from lxml import etree
import requests


# client = pymongo.MongoClient('localhost',27017)
# shidai = client['shidai']
# comments = shidai['comments']




COOKIES ='__mta=256752180.1554272415181.1554273874702.1554282586785.3; cityInfo=%7B%22cityId%22%3A1%2C%22cityName%22%3A%22%E4%B8%8A%E6%B5%B7%22%2C%22provinceId%22%3A0%2C%22parentCityId%22%3A0%2C%22cityOrderId%22%3A0%2C%22isActiveCity%22%3Afalse%2C%22cityEnName%22%3A%22shanghai%22%2C%22cityPyName%22%3Anull%2C%22cityAreaCode%22%3Anull%2C%22cityAbbrCode%22%3Anull%2C%22isOverseasCity%22%3Afalse%2C%22isScenery%22%3Afalse%2C%22TuanGouFlag%22%3A0%2C%22cityLevel%22%3A0%2C%22appHotLevel%22%3A0%2C%22gLat%22%3A0%2C%22gLng%22%3A0%2C%22directURL%22%3Anull%2C%22standardEnName%22%3Anull%7D; _lxsdk_cuid=169e1c3fe45c8-0f754e083bee5c-7a1437-1fa400-169e1c3fe45c8; _lxsdk=169e1c3fe45c8-0f754e083bee5c-7a1437-1fa400-169e1c3fe45c8; _hc.v=8c5f514c-2752-fba0-ff6a-98b837acea0a.1554270912; selectLevel=%7B%22level1%22%3A%221%22%2C%22level2%22%3A%222%22%7D; aburl=1; cy=1; cye=shanghai; _dp.ac.v=8f2de5eb-4671-48a9-a5c5-a385de91ead1; dper=49309ed75899790a8e62c349b50bb374e1aad5d35f033731a577248f0db0f6b6a2a021d7d8a5b9e612c6cb74e948b24ce28814fd96cd8ee773a7cac2553180d1e7a5c110b9b65f7d960dcc7ed7759bf4397084008e19aa9d473980a1d944a937; ua=%E5%92%A9%E5%92%A9%E5%92%A9%E9%85%B1; ctu=41c8e4152f0f10ae8cfafba2c05747080a291cbec5eca405b4ffa5d152eaa12a; ll=7fd06e815b796be3df069dec7836c3df; _lxsdk_s=169e5b9ac11-03d-353-1e0%7C%7C886'


class DianpingComment:
    font_size = 14
    start_y = 23


    def __init__(self, shop_id, cookies, delay=7, handle_ban=True):
        self.shop_id = shop_id
        self._delay = delay
        self.num = 1
        self._cookies = self._format_cookies(cookies)
        self._css_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
        self._default_headers = {
            'Connection': 'keep-alive',
            'Host': 'www.dianping.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
        self._cur_request_url = 'http://www.dianping.com/shop/{}/review_all/p{}'.format(shop_id,self.num)
        # self._cur_request_url = 'http://www.dianping.com/shop/{}/review_all'.format(shop_id)
        if handle_ban:
            print('不想写跳过验证了')
            # self._browser = self._init_browser()
            # self._handle_ban()

    def run(self):
        self._css_link = self._get_css_link(self._cur_request_url)
        # self._css_link = 'http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/f8657d5087e28b789138b11d4d4790e7.svg'
        self._font_dict = self._get_font_dict(self._css_link)
        self._get_conment_page()


    def _delay_func(self):
        delay_time = random.randint((self._delay - 2) * 10, (self._delay + 2) * 10) * 0.1
        time.sleep(delay_time)

    def _init_browser(self):
        """
            初始化游览器
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get(self._cur_request_url)
        for name, value in self._cookies.items():
            browser.add_cookie({'name': name, 'value': value})
        browser.refresh()
        return browser

    def _handle_ban(self):
        """
            爬取速度过快，出现异常时处理验证
        """
        try:
            self._browser.refresh()
            time.sleep(1)
            button = self._browser.find_element_by_id('yodaBox')
            move_x_offset = self._browser.find_element_by_id('yodaBoxWrapper').size['width']
            webdriver.ActionChains(self._browser).drag_and_drop_by_offset(
                button, move_x_offset, 0).perform()
        except:
            pass

    def _format_cookies(self, cookies):
        cookies = {cookie.split('=')[0]: cookie.split('=')[1]
                   for cookie in cookies.replace(' ', '').split(';')}
        return cookies

    def _get_conment_page(self):
        """
            请求评论页，并将<span></span>样式替换成文字
        """
        while self._cur_request_url:
            self._delay_func()
            print('[{now_time}] {msg}'.format(now_time=datetime.datetime.now(), msg=self._cur_request_url))

            res = requests.get(self._cur_request_url, headers=self._default_headers, cookies=self._cookies)
            while res.status_code !=200:
                cookie = random.choice(COOKIES)
                cookies = self._format_cookies(cookie)
                res = requests.get(self._cur_request_url, headers=self._default_headers, cookies=cookies)
                if res.status_code == 200:
                    break

            html = res.text
            class_set = set()
            for span in re.findall(r'<span class="([a-zA-Z0-9]{5,6})"></span>', html):
                class_set.add(span)
            for class_name in class_set:
                try:
                    html = re.sub('<span class="%s"></span>' % class_name, self._font_dict[class_name], html)

                except:
                    html = re.sub('<span class="%s"></span>' % class_name, '', html)

            print(html)
            break
            # doc = etree.HTML(str(html))

            # self._parse_comment_page(doc)
            #
            # try:
            #     self._default_headers['Referer'] = self._cur_request_url
            #     next_page_url = 'http://www.dianping.com' + doc.xpath('.//a[@class="NextPage"]/@href')[0]
            #     print('next_url:{}'.format(next_page_url))
            # except IndexError:
            #     next_page_url = None
            # print('next_page_url:{}'.format(next_page_url))
            # self._cur_request_url = next_page_url
            # self.num = self.num + 1


    def _data_pipeline(self, data):
        """
            处理数据
        """
        print(data)

    def _parse_comment_page(self, doc):
        """
            解析评论页并提取数据
        """
        for li in doc.xpath('//*[@class="reviews-items"]/ul/li'):



                if li.xpath('.//a[@class="name"]/text()'):
                    name = li.xpath('.//a[@class="name"]/text()')[0].strip('\n\r \t')
                else:
                    name = li.xpath('.//span[@class="name"]/text()')[0].strip('\n\r \t')

                try:
                    star = li.xpath('.//span[contains(./@class, "sml-str")]/@class')[0]
                    star = re.search(r'sml-str(\d+)', star)[1]
                except IndexError:
                    star = 0
                time = li.xpath('.//span[@class="time"]/text()')[0].strip('\n\r \t')
                score = ' '.join(map(lambda s: s.strip('\n\r \t'), li.xpath('.//span[@class="score"]//text()')))
                comment = ''.join(li.xpath('.//div[@class="review-words Hide"]/text()')).strip('\n\r \t')
                if not comment:
                    comment = ''.join(li.xpath('.//div[@class="review-words"]/text()')).strip('\n\r \t')
                data = {
                    'name': name,
                    'comment': comment,
                    'star': star,
                    'score': score,
                    'time': time,
                }
                # if comments.find_one({'name':name}):
                #     print('Insert  Error!')
                # else:
                #     comments.insert(data)
                #     print(data)
                self._data_pipeline(data)



    def _get_css_link(self, url):
        """
            请求评论首页，获取css样式文件
        """
        try:
            print(url)
            res = requests.get(url, headers=self._default_headers, cookies=self._cookies)
            html = res.text
            css_link = re.search(r'<link re.*?css.*?href="(.*?svgtextcss.*?)">', html)
            # css_link = re.findall(r'<link re.*?css.*?href="(.*?svgtextcss.*?)">', html)
            css_link = 'http:' + css_link[1]
            print(css_link)
            return css_link
        except:
            None

    def _get_font_dict(self, url):
        """
            获取css样式对应文字的字典
        """
        res = requests.get(url, headers=self._css_headers)
        html = res.text
        print(html)
        background_image_link = re.findall(r'background-image:.*?\((.*?svg)\)', html)
        for i in background_image_link:
            print(i)
        #经检查，发现css文件中有三个.svg文件，其中最后一个是需要的
        background_image_link = 'http:' + background_image_link[2]
        print('----------' * 40)
        print(background_image_link)
        print('---------------' * 40)
        html = re.sub(r'span.*?\}', '', html)
        group_offset_list = re.findall(r'\.([a-zA-Z0-9]{5,6}).*?round:(.*?)px (.*?)px;', html)
        font_dict_by_offset = self._get_font_dict_by_offset(background_image_link)
        font_dict = {}
        for class_name, x_offset, y_offset in group_offset_list:
            x_offset = x_offset.replace('.0', '')
            y_offset = y_offset.replace('.0', '')


            try:
                font_dict[class_name] = font_dict_by_offset[int(y_offset)][int(x_offset)]

            except:
                font_dict[class_name] = ''
        return font_dict

    def _get_font_dict_by_offset(self, url):
        """
            获取坐标偏移的文字字典, 会有最少两种形式的svg文件（目前只遇到两种）
        """
        res = requests.get(url, headers=self._css_headers)
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
        print(font_dict)




        return font_dict

class Customer(DianpingComment):
    def _data_pipeline(self, data):
        print(data)


if __name__ == "__main__":
    dianping = Customer('76998662', cookies=COOKIES)
    dianping.run()