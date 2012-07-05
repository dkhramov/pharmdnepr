#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose
from scrapy.utils.response import get_base_url
from pharmdnepr.items import PharmacyItem
from urlparse import urljoin
import re


class Apteka24Loader(XPathItemLoader):
    default_input_processor = MapCompose( lambda s: re.sub('\s+', ' ', s.strip()) )
    default_output_processor = TakeFirst()


class Apteka24Spider(CrawlSpider):
    
    name = "apteka24"
    allowed_domains = ["www.apteka24.ua"]
    start_urls = ["http://www.apteka24.ua/dnepropetrovsk/catalog/?page=1"]
    rules = (
             Rule( SgmlLinkExtractor(allow=('catalog\/\?.+')) ),
             Rule( SgmlLinkExtractor(allow=('catalog\/\d{3}_?\d{4}')), 
                   callback='parse_item' ),
             )        


    def parse_item(self, response):

        hxs = HtmlXPathSelector(response)
        l = Apteka24Loader(PharmacyItem(), hxs)
        l.add_xpath('name', '//h1/text()')
        l.add_xpath('vendor', '//tr[@class="tdblue"]/td/text()', 
                              re=ur'Производитель: (.+)')
        l.add_xpath('price', '//span[@id="goods_summ"]/text()')
        l.add_value('link', response.url)
        l.add_xpath('desc', '//div[@class="txt"]')        
        return l.load_item()
