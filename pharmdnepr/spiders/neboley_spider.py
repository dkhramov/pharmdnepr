#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import MapCompose, Join, TakeFirst, Compose
from scrapy.http import Request
from pharmdnepr.items import PharmItem
import re


class NeboleyLoader(XPathItemLoader):
    default_input_processor = MapCompose( lambda s: re.sub('\s+', ' ', s.strip()) )
    default_output_processor = Join()
    
    
class NeboleySpider(CrawlSpider):
    
    name = "neboley"
    allowed_domains = ["neboley.dp.ua"]
    start_urls = ["http://neboley.dp.ua/products"]
    rules = (
             Rule(SgmlLinkExtractor(allow=('page\d+')),
                  follow=True, 
                  callback='parseCatalog'),
             )


    def parseCatalog(self, response):
        
        hxs = HtmlXPathSelector(response)
        
        CatalogRows = hxs.select('//tr/td[ @class="pr_name" ]/a')
        nameList = CatalogRows.select('text()').extract()
        linkList = CatalogRows.select('@href').extract()
        
        for i in range( len(nameList) ) :
            item = PharmItem()
            item['name'] = nameList[i]
            item['link'] = linkList[i]
            yield Request(url      = "".join(["http://neboley.dp.ua",item['link']]),  
                          meta     = item,
                          callback = self.parseItem)
            
            
    def parseItem(self, response):
         
         item = response.meta
         hxs = HtmlXPathSelector(response)
         item['vendor'] = hxs.select('//div[ @class="pharmacy_inforow" ]').re(r'<\/span>(.+)<\/div>')
         item['desc']   = hxs.select('//span[ @style="font-family:times new roman,times,serif;" ]/text()').extract()
         
         numProduct = item['link'].split('/')[-1]
         
         yield Request(url      = "".join(["http://neboley.dp.ua/product/",numProduct,"/2"]),  
                       meta     = item,
                       callback = self.parseItemPrice)
    
         
    def parseItemPrice(self, response): 
    
        item = response.meta
        hxs = HtmlXPathSelector(response)
        l = NeboleyLoader(PharmItem(), hxs)        
        l.add_value('name', item['name'])
        l.add_value('link', "".join(["http://neboley.dp.ua",item['link']]))
        l.add_value('vendor', item['vendor'])
        l.add_value('desc', item['desc'])
        l.add_xpath('price', '//div/table/tbody/tr/td/span[2]/text()',
                             TakeFirst(),
                             Compose(lambda x: re.sub(r',', '.', x)))
        return l.load_item()
