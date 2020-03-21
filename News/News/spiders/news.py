# -*- coding: utf-8 -*-
import scrapy
from News.items import NewsItem


class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['eeada.cn']
    start_urls = ['http://www.eeada.cn/']  # 今日关注

    def parse(self, response):  # 获取新闻列表
        article_list = response.xpath("//*[@id='content']//article")
        # print(article_list)
        for article in article_list:
            item = NewsItem()
            item["title"] = article.xpath(".//h2/a/@title").extract_first()
            item["href"] = article.xpath(".//h2/a/@href").extract_first()
            item["date"] = article.xpath(".//span/text()").extract_first().strip(" ").strip('\r\n')

            yield scrapy.Request(
                item["href"],
                callback=self.parse_detail,
                meta={"item": item}
            )
        # 翻页
        next_url = response.xpath("//*[@id='content']//a[@class='next page-numbers']/@href").extract_first()
        #print(next_url)
        if next_url is not None:
            yield scrapy.Request(
                next_url,
                callback=self.parse
            )

    def parse_detail(self, response):  # 处理详情页
        item = response.meta["item"]
        item["text"] = response.xpath("//div[@id='content']//p//text()").extract()
        item["text"] = [str.strip(" ").strip('\r\n').replace(u'\u3000', u'').replace(u'\xa0', u'') for str in
                        item["text"]]
        item["text"] = ''.join(item["text"])
        item["source"] = "今日关注"
        yield item
