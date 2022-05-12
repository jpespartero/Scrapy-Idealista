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
    city = Field()
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

    # U Tag Data
    municipalityId = Field()
    provinceId = Field()
    locationId = Field()
    locationLevel = Field()
    builtType = Field()
    roomNumber = Field()
    bathNumber = Field()
    hasLift = Field()
    hasParking = Field()
    constructedArea = Field()
    isNewDevelopment = Field()
    isNeedsRenovating = Field()
    isGoodCondition = Field()
    photoNumber = Field()
    videoNumber = Field()
    hasFloorPlan = Field()
    hasHomeStaging = Field()
    hasHomeAppliances = Field()

    ownerType = Field()
    commercialId = Field()
    commercialName = Field()

    time = Field()
