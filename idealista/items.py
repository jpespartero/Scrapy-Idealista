# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class IdealistaItem(Item):

    adid = Field()
    adtype = Field()
    timestamp = Field()

    date = Field()
    link = Field()
    title = Field()
    description = Field()
    last_update = Field()

    #
    user_name = Field()
    is_particular = Field()
    phoneNumber = Field()
    email = Field()

    # Price
    price = Field()
    discount = Field()
    previous_price = Field()

    # Location
    country = Field()
    district = Field()
    address = Field()
    latitude = Field()
    longitude = Field()
    postal_code = Field()

    # Characteristis
    size_m2 = Field()
    rooms = Field()
    bathrooms = Field()
    floor = Field()
    has_parking = Field()
    has_elevator = Field()
    has_pool = Field()
    has_terrace = Field()
    is_exterior = Field()
    is_second_hand = Field()
    energy_certificate_consumption = Field()
    energy_certificate_emissions = Field()
