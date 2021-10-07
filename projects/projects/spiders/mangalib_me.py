from .constants.mangalib_me import *

import json
import re
from datetime import datetime
from time import mktime
import scrapy
from w3lib.url import add_or_replace_parameter
from scrapy import Request
from scrapy.selector import Selector
from copy import deepcopy
import requests


class MangalibMeSpider(scrapy.Spider):
    name = 'mangalib_me'
    domain = 'https://mangalib.me/'
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 5,
        'DOWNLOAD_TIMEOUT': 30,
        'DOWNLOAD_HANDLERS': {
            'https': 'scrapy.core.downloader.handlers.http2.H2DownloadHandler',
        },
        'DOWNLOADER_MIDDLEWARES': {
        }
    }

    @staticmethod
    def get_timestamp(dt=None):
        if not dt:
            dt = datetime.now().timetuple()
        return int(mktime(dt))

    def get_result_container(self):
        result = {
            "timestamp": self.get_timestamp(),
            "id": "",
            "slug": "",
            "title_ru": "",
            "title_en": "",
            "chapters_count": "",
            "chapter_id": "",
            "translator": "",
            "images": [],
        }
        return result

    @staticmethod
    def get_manga_parameters(manga=None, result=None):
        result["id"] = manga['id']
        result["slug"] = manga['slug']
        result["title_ru"] = manga['rusName']
        result["title_en"] = manga['engName']
        result["chapters_count"] = manga['chapters_count']
        return result

    def start_requests(self):
        for url in START_URLS:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        result = self.get_result_container()
        data = re.search(r'window\.__DATA__ = (\{.+\})', response.text)
        data = json.loads(data.group(1))
        manga = data['manga']
        result.update(self.get_manga_parameters(manga, result))

        chapters = data['chapters']['list']
        for chapter in chapters:
            volume, number = chapter['chapter_volume'], chapter['chapter_number']
            url = self.domain + result['slug'] + f"/v{volume}/c{number}?page=2"
            yield Request(url=url, callback=self.parse_chapters,
                          meta={'data': {'result': result, 'volume': volume, 'number': number}})

    def parse_chapters(self, response):
        image = response.xpath(IMAGE).get()
        if 'gif' not in image:
            img_data = requests.get(image).content
            with open('image_name.png', 'wb') as handler:
                handler.write(img_data)