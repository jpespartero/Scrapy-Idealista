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
    #start_urls = ['https://www.idealista.com/venta-viviendas/sevilla/sevilla-este/']
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

    def parse_ads_index_page(self, response):

        # Iterate over the house ids to get the details
        house_ids = IdealistaSpider.get_house_ids(response);
        for house_id in house_ids:
            item = IdealistaSpider.parse_house_info(self, response, house_id);
            yield item

    def get_house_ids(response):
        house_ids = response.xpath("//*[@data-adid]/@data-adid").getall()
        return house_ids

    def parse_house_info(self, response, house_id):
        house_info = response.xpath("//*[@data-adid=" + house_id + "]")
        house_info_data = house_info.xpath("//*[@data-adid=" + house_id + "]/*[@class='item-info-container']")

        date = datetime.utcnow().strftime('%Y-%m-%d')
        link = IdealistaSpider.parse_link(house_info_data)
        price = IdealistaSpider.parse_price(house_info_data)
        title = IdealistaSpider.parse_title(house_info_data)
        discount = IdealistaSpider.parse_discount(house_info_data)
        sqft_m2 = IdealistaSpider.parse_sqft_m2(house_info_data)
        rooms = IdealistaSpider.parse_rooms(house_info_data)
        floor_elevator = IdealistaSpider.parse_floor_elevator(house_info_data)

        return IdealistaItem(adid=house_id,
            date=date,
            link=link,
            price=price,
            address=title,
            discount=discount,
            sqft_m2=sqft_m2,
            rooms=rooms,
            floor_elevator=floor_elevator)

    def parse_link(house_info_data):
        default_url = 'http://idealista.com'
        house_link = house_info_data.xpath('a/@href').get()
        link = default_url + str(house_link)
        return link;

    def parse_price(house_info_data):
        price = house_info_data.xpath("//*[@class='price-row ']/span[@class='item-price h2-simulated']/text()").get()
        price = float(price.replace('.', '').strip())
        return price;

    def parse_title(house_info_data):
        title = house_info_data.xpath('a/@title').extract().pop().encode('iso-8859-1')
        return title;

    def parse_discount(house_info_data):
        discount = house_info_data.xpath("//*[@class='price-row ']/span[@class='item-price h2-simulated']/text()").get()

        #discounts_xpath = response.xpath("//*[@class='price-row ']")
        #discounts = [0 if len(discount.xpath("./*[@class='item-price-down icon-pricedown']/text()").extract()) < 1
        #             else discount.xpath("./*[@class='item-price-down icon-pricedown']/text()").extract().pop().replace(
        #    '.', '').strip().split(' ').pop(0)
        #             for discount in discounts_xpath]

        return discount;

    def parse_sqft_m2(house_info_data):
        title = house_info_data.xpath("//*[@class='price-row ']/span[@class='item-price h2-simulated']/text()").get()

        #sqfts_m2 = [float(
        #    flat.xpath('span[@class="item-detail"]/small[starts-with(text(),"m")]/../text()').extract().pop().replace(
        #        '.', '').strip())
        #            if len(flat.xpath('span[@class="item-detail"]/small[starts-with(text(),"m")]')) == 1
        #            else None
         #           for flat in info_flats_xpath]

        return title;

    def parse_rooms(house_info_data):
        rooms = house_info_data.xpath("//*[@class='price-row ']/span[@class='item-price h2-simulated']/text()").get()

        #rooms = [int(flat.xpath(
        #    'span[@class="item-detail"]/small[contains(text(),"hab.")]/../text()').extract().pop().strip())
        #         if len(flat.xpath('span[@class="item-detail"]/small[contains(text(),"hab.")]')) == 1
        #         else None
        #         for flat in info_flats_xpath]

        return rooms;

    def parse_floor_elevator(house_info_data):
        title = house_info_data.xpath("//*[@class='price-row ']/span[@class='item-price h2-simulated']/text()").get()

        #floors_elevator = [flat.xpath('string(span[@class="item-detail"][last()])').extract().pop().strip()
        #                   for flat in info_flats_xpath]

        return title;

    # def parse_house_ad_single_page(self, response):

    #Overriding parse_start_url to get the first page
    parse_start_url = parse_ads_index_page


