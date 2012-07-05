#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import MapCompose, Join
from scrapy.http import Request
from pharmdnepr.items import PharmacyItem
import re


class AmaLoader(XPathItemLoader):
    default_input_processor = MapCompose( lambda s: re.sub('\s+', ' ', s.strip()) )
    default_output_processor = Join()


class AmaSpider(CrawlSpider):
    
    name = "ama"
    allowed_domains = ["ama.dp.ua"]
    start_urls = ["http://ama.dp.ua/Price/Retail/default.asp?action=all&arg1=&page=1"]
    rules = (
             Rule( SgmlLinkExtractor(allow=(r'page=\d+')), 
                   follow=True, 
                   callback='parseCatalog' ),
             )


    def parseCatalog(self, response):
        
        hxs = HtmlXPathSelector(response)
        CatalogRows = hxs.select('//table[ @id="result" ]/tbody/tr')
        nameList = CatalogRows.select('td[2]/a/text()').extract()
        linkList = CatalogRows.select('td[2]/a/@href').extract()
        priceList = CatalogRows.select('td[4]/text()').extract()
        
        for i in range( len(nameList) ) :
            item = PharmacyItem()
            item['name']  = nameList[i]
            item['link']  = "".join(["http://ama.dp.ua/",linkList[i]])
            item['price'] = priceList[i]
            yield Request(url      = "".join(["http://ama.dp.ua/Price/Retail/", 
                                      linkList[i]]),  
                          meta     = item,
                          callback = self.parseItem)


    def parseItem(self, response):

        item = response.meta        
        hxs = HtmlXPathSelector(response)
        
        item['vendor'] = hxs.select('//table/tr/td/div/p[1]').re(ur'<b>Производитель:<\/b>(.+?)<br')

        instr = hxs.select('//table/tr/td/div/p/a/@href').extract()
        if instr:
            yield Request(url      = "".join(["http://ama.dp.ua/Price/Retail/", 
                                       instr[0]]),  
                          meta     = item,
                          callback = self.parseItemDescription)
                          
        l = AmaLoader(PharmacyItem(), hxs)
        l.add_value('name', item['name'])
        l.add_value('link', item['link'])
        l.add_value('vendor', item['vendor'])
        l.add_value('price', item['price'])
        l.add_value('desc', u'')
        yield l.load_item()


    def parseItemDescription(self, response):
        
        item = response.meta
        hxs = HtmlXPathSelector(response)
        l = AmaLoader(PharmacyItem(), hxs)
        l.add_value('name', item['name'])
        l.add_value('link', item['link'])
        l.add_value('vendor', item['vendor'])
        l.add_value('price', item['price'])
        l.add_xpath('desc', '/html/body/p')
        return l.load_item()
