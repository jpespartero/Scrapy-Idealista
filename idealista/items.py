# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IdealistaItem(scrapy.Item):
    #Matching variables of every flat to be scrapped
    adid = scrapy.Field()
    date = scrapy.Field()
    link = scrapy.Field()
    title = scrapy.Field()

    price = scrapy.Field()
    discount = scrapy.Field()

    size_m2 = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    parking = scrapy.Field()

