# -*- coding: utf-8 -*-

# Scrapy settings for idealista project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

from .proxies import get_proxies
from idealista.elastic.scrapyelasticsearch import ElasticSearchPipeline

###########################
# Main configuration
###########################

BOT_NAME = 'idealista'

SPIDER_MODULES = ['idealista.spiders']
NEWSPIDER_MODULE = 'idealista.spiders'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620
}

DEFAULT_REQUEST_HEADERS = {
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

FEED_EXPORT_ENCODING='latin-1'
DOWNLOAD_DELAY = 3
DOWNLOAD_TIMEOUT = 10


###########################
# User agent configurarion
###########################

USER_AGENTS = [
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'),
    #('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'),
    #('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0')
    
    # Add more user agents which actually work nowadays
]

#########################
# Proxies configuration
#########################

#RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]
#ROTATING_PROXY_PAGE_RETRY_TIMES = 99999999999 # TODO: is it possible to setup this parameter with no limit?
#ROTATING_PROXY_LIST = get_proxies()


#########################
# Elastic search configuration
#########################

ITEM_PIPELINES = {
    #'scrapyelasticsearch.scrapyelasticsearch.ElasticSearchPipeline': 500
    #'idealista.elastic.scrapyelasticsearch.ElasticSearchPipeline': 500
}

ELASTICSEARCH_SERVERS = ['http://elastic:changeme@localhost:9200']
ELASTICSEARCH_INDEX = 'idealista-debug2'
ELASTICSEARCH_INDEX_DATE_FORMAT = '%Y-%m'
ELASTICSEARCH_UNIQ_KEY = 'adid'

# can also accept a list of fields if need a composite key
#ELASTICSEARCH_UNIQ_KEY = ['url', 'id']

