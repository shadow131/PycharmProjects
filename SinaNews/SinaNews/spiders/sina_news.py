# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from SinaNews.items import SinanewsItem


class SinaNewsSpider(scrapy.Spider):
    name = 'sina_news'
    allowed_domains = ['sina.cn']
    start_urls = ['https://news.sina.cn/gj', 'https://news.sina.cn/gn']

    def parse(self, response):
        # 创建chrome浏览器驱动，无头模式
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
                                  chrome_options=chrome_options)
        # 加载界面
        if response.url == self.start_urls[0]:
            driver.get(self.start_urls[0])
        if response.url == self.start_urls[1]:
            driver.get(self.start_urls[1])
        time.sleep(3)
        # 获取页面初始高度
        js = "return action=document.body.scrollHeight"
        height = driver.execute_script(js)
        # 将滚动条调整至页面底部
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(5)
        # 定义初始时间戳(秒)
        t1 = int(time.time())
        # 定义循环标识，用于终止while循环
        status = True
        # 重试次数
        num = 0
        while status:
            # 获取当前时间戳(秒)
            t2 = int(time.time())
            # 判断时间初始时间戳和当前时间戳相差是否大于30秒，小于30秒则下拉滚动条
            if t2 - t1 < 5:
                new_height = driver.execute_script(js)
                if new_height > height:
                    time.sleep(1)
                    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                    # 重置初始页面高度
                    height = new_height
                    # 重置初始时间戳，重新计时
                    t1 = int(time.time())
            elif num < 3:  # 当超过30秒页面高度仍然没有更新时，进入重试逻辑，重试3次，每次等待30秒
                time.sleep(3)
                num = num + 1
            else:  # 超时并超过重试次数，程序结束跳出循环，并认为页面已经加载完毕!
                # print("滚动条已经处于页面最下方!")
                status = False
                # 滚动条调整至页面顶部
                driver.execute_script('window.scrollTo(0, 0)')
                break
        # 打印页面源码
        # content = driver.page_source
        article_list = driver.find_elements_by_xpath("//section[@id='j_items_list']//section")
        # print(article_list)
        for article in article_list:
            item = SinanewsItem()
            item["title"] = article.find_element_by_xpath("./a//h2").text
            item["href"] = article.find_element_by_xpath("./a").get_attribute("href")
            #print(item["title"])
            #print(item["href"])
            yield scrapy.Request(
                item["href"],
                callback=self.parse_detail,
                meta={"item": item}
            )

    def parse_detail(self, response):  # 处理详情页

        item = response.meta["item"]
        item["date"] = response.xpath(".//section[@class='j_main_art']//article//time//text()").extract()
        item["date"] = ''.join(item["date"]).strip().replace('\t','').replace('\n',' ')
        # if item["date"] is None:
        #     item["date"] = response.xpath(
        #         ".//section/article//div/figcaption/figure/time[@class='weibo_time']/span//text()").extract_first()
        #     print(item["date"])
        item["text"] = response.xpath(
            ".//section[@class='j_main_art']//article//p[@class='art_p' and position()>1]//text()").extract()
        item["text"] = [str.strip(" ").strip('\r\n').replace(u'\u3000', u'').replace(u'\xa0', u'') for str in
                        item["text"]]
        item["text"] = ''.join(item["text"])
        item["source"] = response.xpath(".//section[@class='j_main_art']//article//time/cite/text()").extract_first()
        if item["source"] is None:
            item["source"] = response.xpath(
                ".//section/article//div/figcaption/figure/h2[@class='weibo_user']//text()").extract_first()
            # print(item["source"])
        if item["source"] is None:
            item["source"] = item["date"][20:]
        item["date"] = item["date"][0:19]
        #print(item)
        yield item
