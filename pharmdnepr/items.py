#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import MapCompose,TakeFirst
import re


def parseDesc(x):
    
    match = re.search(ur'не найдена', x)
    if match:
        return u''
    x = re.sub(ur'Купить.+', ' ', x )
    return x


class PharmItem(Item):
    
    name   = Field()
    link   = Field()
    vendor = Field()
    price  = Field()
    desc   = Field()


class PharmacyItem(PharmItem):
    
    desc   = Field( input_processor=MapCompose(parseDesc) )
