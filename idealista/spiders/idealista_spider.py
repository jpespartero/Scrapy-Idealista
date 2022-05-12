__author__ = ''

import logging

import scrapy
from scrapy import Request

from idealista.items import IdealistaItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime


class IdealistaSpider(CrawlSpider):
    name = "idealista"
    allowed_domains = ["idealista.com"]

    ########################################################################
    #  Add the url to crawl in the start_urls variable
    start_urls = ['https://www.idealista.com/alquiler-viviendas/tres-cantos-madrid/']
    # start_urls = ['https://www.idealista.com/venta-viviendas/tres-cantos-madrid/']

    #######################################################################
    headers = {
        'authority': 'www.idealista.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'es-ES,es;q=0.9',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1'
    }
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'

    custom_settings = {
        'DOWNLOAD_TIMEOUT': '10',
        'DOWNLOAD_DELAY': '1',
    }
    ########################################################################

    rules = (
        # Filter all the flats paginated by the website following the pattern indicated
        Rule(LinkExtractor(restrict_xpaths="//a[@class='icon-arrow-right-after']"),
             callback='parse_ads_index_page',
             follow=True),
    )

    scan_single_ads = True

    # Iterate over the house ids in the index page to get the details for each house advertising
    def parse_ads_index_page(self, response):

        adtype = IdealistaSpider.get_ad_type(self, response)

        house_ids = IdealistaSpider.get_house_ids(self, response)
        for house_id in house_ids:
            item = IdealistaSpider.parse_house_info(self, response, house_id)
            item['adtype'] = adtype

            # TODO: Hay que ver como pasar un parametro exerno
            if self.scan_single_ads == True:
                request = IdealistaSpider.generate_single_house_page_request(self, item)
                yield request
            else:
                yield item

    def get_ad_type(selfself, response):
        if 'alquiler' in response.url:
            ad_type = 'rent'
        else:
            ad_type = 'sale'
        return ad_type

    def get_house_ids(self, response):
        house_ids = response.xpath("//*[@data-adid]/@data-adid").getall()
        return house_ids

    def parse_house_info(self, response, house_id):
        house_info = response.xpath("//*[@data-adid=" + house_id + "]")
        house_info_data = house_info.xpath("//*[@data-adid=" + house_id + "]/*[@class='item-info-container']")[0]

        timestamp = datetime.utcnow().isoformat()
        date = datetime.utcnow().strftime('%Y-%m-%d')
        link = IdealistaSpider.parse_link(self, house_info_data)
        price = IdealistaSpider.parse_price(self, house_info_data)
        title = IdealistaSpider.parse_title(self, house_info_data)
        previous_price = IdealistaSpider.parse_previous_price(self, house_info_data)
        discount = IdealistaSpider.parse_discount(self, house_info_data)
        size_m2 = IdealistaSpider.parse_size_m2(self, house_info_data)
        rooms = IdealistaSpider.parse_rooms(self, house_info_data)
        floor = IdealistaSpider.parse_floor(self, house_info_data)
        has_parking = IdealistaSpider.parse_parking_included(self, house_info_data)

        item = IdealistaItem(timestamp=timestamp,
                             adid=house_id,
                             date=date,
                             link=link,
                             title=title,
                             price=price,
                             previous_price=previous_price,
                             discount=discount,
                             size_m2=size_m2,
                             rooms=rooms,
                             floor=floor,
                             has_parking=has_parking)

        return item

    def parse_link(self, house_info_data):
        default_url = 'https://www.idealista.com'
        house_link = house_info_data.xpath('a/@href').get()
        link = default_url + str(house_link)
        return link

    def parse_price(self, house_info_data):
        price = house_info_data.xpath("*[@class='price-row ']/span[@class='item-price h2-simulated']/text()").get()
        price = float(price.replace('.', '').strip())
        return price

    def parse_title(self, house_info_data):
        title = house_info_data.xpath('a/@title').extract().pop()   #.encode('iso-8859-1')
        return title

    def parse_previous_price(self, house_info_data):
        pricedown_info = house_info_data.xpath("*[@class='price-row ']/span[@class='pricedown']")
        if len(pricedown_info) == 0:
            previous_price = 0
        else:
            previous_price = pricedown_info.xpath("*[@class='pricedown_price']/text()").get()
            previous_price = float(previous_price.replace('.', '').replace('€', '').strip())
        return previous_price

    def parse_discount(self, house_info_data):
        pricedown_info = house_info_data.xpath("*[@class='price-row ']/span[@class='pricedown']")
        if len(pricedown_info) == 0:
            discount = 0
        else:
            discount = pricedown_info.xpath("*[@class='pricedown_icon icon-pricedown']/text()").get()
            discount = float(discount.replace('.', '').replace('%', '').strip())
        return discount

    def parse_size_m2(self, house_info_data):
        item_details = house_info_data.xpath('*[@class="item-detail-char"]')[0]
        size_m2 = item_details.xpath('*[@class="item-detail"]/small[starts-with(text(),"m")]/../text()').get()
        size_m2 = float(size_m2.replace('.', '').strip())
        return size_m2

    def parse_rooms(self, house_info_data):
        item_details = house_info_data.xpath('*[@class="item-detail-char"]')[0]
        rooms = item_details.xpath('*[@class="item-detail"]/small[starts-with(text(),"hab.")]/../text()').get()
        if rooms is None:
            rooms = 0
        return rooms

    def parse_floor(self, house_info_data):
        item_details = house_info_data.xpath('*[@class="item-detail-char"]')[0]
        floor = item_details.xpath('*[@class="item-detail"][starts-with(text(), "Planta")]/text()').get()
        if floor is not None:
            floor = floor.replace('Planta', '').replace('º', '').replace('ª', '').strip()
        else:
            floor = 0
        return floor

    def parse_parking_included(self, house_info_data):
        parking_info = house_info_data.xpath("*[@class='price-row ']/span[@class='item-parking']")
        if len(parking_info) == 0:
            parking = False
        else:
            parking = True
        return parking

    def generate_single_house_page_request(self, item):

        # Open the house page to get the details
        request = Request(
            url=item['link'],
            callback=self.parse_single_house_ad_page,
            # headers=self.headers,
        )
        request.cb_kwargs['item'] = item
        return request

    def parse_single_house_ad_page(self, response, item):
        item['city'] = IdealistaSpider.parse_city(self, response)
        item['address'] = IdealistaSpider.parse_address(self, response)

        # Parse data in javascript
        script_data = IdealistaSpider.get_java_script_data(self, response)
        if script_data is not None:

            # Parse location
            mapConfig_value = IdealistaSpider.get_script_variable_value(self, script_data, 'mapConfig')
            item['latitude'] = IdealistaSpider.get_json_value(self, mapConfig_value, 'latitude')
            item['longitude'] = IdealistaSpider.get_json_value(self, mapConfig_value, 'longitude')

            # Parse U-TAG data
            utag_value = IdealistaSpider.get_script_variable_value(self, script_data, 'utag_data')
            item['municipalityId'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'municipalityId')
            item['provinceId'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'provinceId')
            item['locationId'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'locationId')
            item['locationLevel'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'locationLevel')
            item['builtType'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'builtType')

            #item['price'] = IdealistaSpider.get_json_value(self, mapConfig_value, 'price')

            characteristics_data = IdealistaSpider.get_json_data(self, utag_value, 'characteristics')
            item['roomNumber'] = IdealistaSpider.get_json_value_quote(self, characteristics_data, 'roomNumber')
            item['bathNumber'] = IdealistaSpider.get_json_value_quote(self, characteristics_data, 'bathNumber')
            item['hasLift'] = IdealistaSpider.get_json_value_quote(self, characteristics_data, 'hasLift')
            item['hasParking'] = IdealistaSpider.get_json_value_quote(self, characteristics_data, 'hasParking')
            item['constructedArea'] = IdealistaSpider.get_json_value_quote(self, characteristics_data, 'constructedArea')

            condition_data = IdealistaSpider.get_json_data(self, utag_value, 'condition')
            item['isNewDevelopment'] = IdealistaSpider.get_json_value_quote(self, condition_data, 'isNewDevelopment')
            item['isNeedsRenovating'] = IdealistaSpider.get_json_value_quote(self, condition_data, 'isNeedsRenovating')
            item['isGoodCondition'] = IdealistaSpider.get_json_value_quote(self, condition_data, 'isGoodCondition')

            item['photoNumber'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'photoNumber')
            item['videoNumber'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'videoNumber')
            item['hasFloorPlan'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'hasFloorPlan')
            # item['has3Dtour'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'has3Dtour')
            # item['hasHomeStaging'] = IdealistaSpider.get_json_value_quote(self, utag_value, 'hasHomeStaging')

            owner_data = IdealistaSpider.get_json_data(self, utag_value, 'owner')
            item['ownerType'] = IdealistaSpider.get_json_value_quote(self, owner_data, 'type')
            item['commercialId'] = IdealistaSpider.get_json_value_quote(self, owner_data, 'commercialId')
            item['commercialName'] = IdealistaSpider.get_json_value_quote(self, owner_data, 'commercialName')

            # Post creation date??
            post_data = IdealistaSpider.get_json_data(self, utag_value, 'post')
            item['time'] = IdealistaSpider.get_json_value_quote(self, post_data, 'time')

        yield item


    def parse_city(self, response):
        city = response.xpath('//*[@id="sMap"]/text()').get()
        if city is not None:
            self.logger.info("City: %s", city)
        else:
            city = None
        return city

    def parse_address(self, response):
        address_data = response.xpath('//*[@class="header-map-list"]/text()')
        address = ''.join([
            address_line.get()
            for address_line in address_data
        ])

        return address

    def get_java_script_data(self, response):
        try:
            script = ''.join([
                text.get()
                for text in response.css('script::text')
                # if 'maps' in text.get()
            ])
        except:
            script = None
            logging.WARN("Error getting javascript data")
        return script

    def get_json_value(self, string, json_key):
        key_start = string.find(json_key)
        value_start = string.find("'", key_start)
        value_end = string.find("'", value_start + 1)
        return string[value_start + 1:value_end]

    def get_json_data(self, string, json_key):
        key_start = string.find(json_key)
        value_start = string.find("{", key_start)
        value_end = string.find("}", value_start + 1)
        return string[value_start + 1:value_end]

    def get_json_value_quote(self, string, json_key):
        key_start = string.find(json_key)
        value_start = string.find(':', key_start)
        quote_start = string.find('"', value_start + 1)
        quote_end = string.find('"', quote_start + 1)
        return string[quote_start + 1:quote_end]

    def get_script_variable_value(self, string, variable_name):
        variable_start = string.find(variable_name)
        value_start = string.find("=", variable_start)
        value_end = string.find(";", value_start + 1)
        return string[value_start + 1:value_end]

    # Overriding parse_start_url to get the first page
    parse_start_url = parse_ads_index_page
