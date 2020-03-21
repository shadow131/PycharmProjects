# -*- coding: utf-8 -*-
import scrapy
from scrapy import item


class ItcastSpider(scrapy.Spider):
    name = 'itcast'
    allowed_domains = ['itcast.cn']
    start_urls = ['http://www.itcast.cn/channel/teacher.shtml']

    def parse(self, response):
        # filename = "teacher.html"
        # open(filename, 'w',encoding='utf-8').write(response.text)
        li_list = response.xpath("//div[@class='tea_con']//li   ")
        for li in li_list:
            item = {}
            item['name'] = li.xpath(".//h3/text()").extract_first()
            # print(dir(response))
            item['title'] = li.xpath(".//h4/text()").extract_first()
            # item['info'] = li.xpath(".//p/text()").extract_first()
            yield item

