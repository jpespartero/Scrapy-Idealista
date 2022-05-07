__author__ = 'David Carrasco'

import scrapy
from scrapy.crawler import CrawlerProcess
from idealista.items import IdealistaItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime



class IdealistaSpider(CrawlSpider):
    name = "idealista"
    allowed_domains = ["idealista.com"]

    ########################################################################
    ###       Add the url to crawl in the start_urls variable           ###
    ########################################################################
    # start_urls = ['https://www.idealista.com/venta-viviendas/sevilla/sevilla-este/']
    start_urls = ['https://www.idealista.com/alquiler-viviendas/tres-cantos-madrid/']

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
        'DOWNLOAD_DELAY': '5',
    }
    ########################################################################

    rules = (
        # Filter all the flats paginated by the website following the pattern indicated
        Rule(LinkExtractor(restrict_xpaths=("//a[@class='icon-arrow-right-after']")),
             callback='parse_ads_index_page',
             follow=True),
    )

    # Iterate over the house ids in the index page to get the details for each house advertising
    def parse_ads_index_page(self, response):
        house_ids = IdealistaSpider.get_house_ids(response);
        for house_id in house_ids:
            item = IdealistaSpider.parse_house_info(self, response, house_id);
            yield item

    def get_house_ids(response):
        house_ids = response.xpath("//*[@data-adid]/@data-adid").getall()
        return house_ids

    def parse_house_info(self, response, house_id):
        house_info = response.xpath("//*[@data-adid=" + house_id + "]")
        house_info_data = house_info.xpath("//*[@data-adid=" + house_id + "]/*[@class='item-info-container']")[0]

        date = datetime.utcnow().strftime('%Y-%m-%d')
        link = IdealistaSpider.parse_link(self, house_info_data)
        price = IdealistaSpider.parse_price(self,house_info_data)
        title = IdealistaSpider.parse_title(self, house_info_data)
        discount = IdealistaSpider.parse_discount(self,house_info_data)
        size_m2 = IdealistaSpider.parse_size_m2(self,house_info_data)
        rooms = IdealistaSpider.parse_rooms(self,house_info_data)
        floor = IdealistaSpider.parse_floor(self,house_info_data)
        parking = IdealistaSpider.parse_parking_included(self,house_info_data)

        item = IdealistaItem(adid=house_id,
                             date=date,
                             link=link,
                             title=title,
                             price=price,
                             discount=discount,
                             size_m2=size_m2,
                             rooms=rooms,
                             floor=floor,
                             parking=parking)

        # Open the house page to get the details
        #IdealistaSpider.crawl_single_house_page(self, item)

        return item;


    def parse_link(self, house_info_data):
        default_url = 'http://idealista.com'
        house_link = house_info_data.xpath('a/@href').get()
        link = default_url + str(house_link)
        return link

    def parse_price(self, house_info_data):
        price = house_info_data.xpath("*[@class='price-row ']/span[@class='item-price h2-simulated']/text()").get()
        price = float(price.replace('.', '').strip())
        return price

    def parse_title(self, house_info_data):
        title = house_info_data.xpath('a/@title').extract().pop().encode('iso-8859-1')
        return title

    def parse_discount(self, house_info_data):
        pricedown_info = house_info_data.xpath("*[@class='price-row ']/span[@class='pricedown']")
        if len(pricedown_info) == 0:
            discount = 0
        else:
            discount = pricedown_info.xpath("*[@class='pricedown_price']/text()").get()
            discount = float(discount.replace('.', '').replace('€','').strip())
        return discount

    def parse_size_m2(self, house_info_data):
        item_details = house_info_data.xpath('*[@class="item-detail-char"]')[0]
        size_m2 = item_details.xpath('*[@class="item-detail"]/small[starts-with(text(),"m")]/../text()').get()
        size_m2 = float(size_m2.replace('.', '').strip())
        return size_m2

    def parse_rooms(self, house_info_data):
        item_details = house_info_data.xpath('*[@class="item-detail-char"]')[0]
        rooms = item_details.xpath('*[@class="item-detail"]/small[starts-with(text(),"hab.")]/../text()').get()
        return rooms

    def parse_floor(self, house_info_data):
        item_details = house_info_data.xpath('*[@class="item-detail-char"]')[0]
        floor = item_details.xpath('*[@class="item-detail"][3]/text()').get()
        return floor

    def parse_parking_included(self, house_info_data):
        parking_info = house_info_data.xpath("*[@class='price-row ']/span[@class='item-parking']")
        if len(parking_info) == 0:
            parking = False
        else:
            parking = True
        return parking

    def crawl_single_house_page(self, item):

        # Open the house page to get the details
        response = scrapy.Request(
            url=item['link'],
            headers=self.headers,
        )
        #parse_house_ad_single_page(self, response, item)

    def parse_house_ad_single_page(self, response, item):

        return 0

    # Overriding parse_start_url to get the first page
    parse_start_url = parse_ads_index_page