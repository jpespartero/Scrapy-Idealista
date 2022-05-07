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

    	# Necessary in order to create the whole link towards the website
        default_url = 'http://idealista.com'

        # Get the number of results
        house_ids = IdealistaSpider.get_house_ids(response);

        # Iterate over the house ids to get the details


        # Iterate over the house ids to enter in the single detailed pages

        info_flats_xpath = response.xpath("//*[@class='item-info-container']")
        prices_flats_xpath = response.xpath("//*[@class='price-row ']/span[@class='item-price h2-simulated']/text()")
        discounts_xpath = response.xpath("//*[@class='price-row ']")

        links = [str(''.join(default_url + link.xpath('a/@href').extract().pop()))
                 for link in info_flats_xpath]

        prices = [float(flat.extract().replace('.','').strip())
                 for flat in prices_flats_xpath]
                 
        discounts = [0 if len(discount.xpath("./*[@class='item-price-down icon-pricedown']/text()").extract()) < 1
                     else discount.xpath("./*[@class='item-price-down icon-pricedown']/text()").extract().pop().replace('.','').strip().split(' ').pop(0) 
                     for discount in discounts_xpath]
        
        addresses = [address.xpath('a/@title').extract().pop().encode('iso-8859-1')
		     for address in info_flats_xpath]
                     
        rooms = [int(flat.xpath('span[@class="item-detail"]/small[contains(text(),"hab.")]/../text()').extract().pop().strip()) 
                 if len(flat.xpath('span[@class="item-detail"]/small[contains(text(),"hab.")]')) == 1 
                 else None 
                 for flat in info_flats_xpath]
                 
        sqfts_m2 = [float(flat.xpath('span[@class="item-detail"]/small[starts-with(text(),"m")]/../text()').extract().pop().replace('.','').strip())
                    if len(flat.xpath('span[@class="item-detail"]/small[starts-with(text(),"m")]')) == 1 
                    else None 
                    for flat in info_flats_xpath]
                    
        floors_elevator = [flat.xpath('string(span[@class="item-detail"][last()])').extract().pop().strip()
                           for flat in info_flats_xpath]
                           
        for flat in zip(house_ids, links, prices, addresses, discounts, sqfts_m2, rooms, floors_elevator):
            item = IdealistaItem(adid=flat[0],
                date=datetime.now().strftime('%Y-%m-%d'),
				link=flat[1],
                price=flat[2],
                address=flat[3],
                discount=flat[4],
                sqft_m2=flat[5],
                rooms=flat[6],
                floor_elevator = flat[7])
            yield item


    #def parse_house_info(self, response):



    #def parse_house_ad_single_page(self, response):



    # This function gets the number of flats announced in this webpage
    def get_house_ids(response):
        house_ids = response.xpath("//*[@data-adid]/@data-adid").getall()
        return house_ids

    #def get_ad_links(response):
    #    return response.xpath("//*[@data-adid]/@data-adid").getall()

    #def get_ad_titles(response):
    #    return response.xpath("//*[@data-adid]/@data-adid").getall()


    #Overriding parse_start_url to get the first page
    parse_start_url = parse_ads_index_page

# Only for debug
#process = CrawlerProcess()
#process.crawl(IdealistaSpider)
#process.start()

