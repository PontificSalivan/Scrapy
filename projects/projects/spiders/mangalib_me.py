import scrapy


class MangalibMeSpider(scrapy.Spider):
    name = 'mangalib_me'
    allowed_domains = ['mangalib.me']
    start_urls = ['http://mangalib.me/']

    def parse(self, response):
        pass
