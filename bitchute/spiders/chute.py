import time

import scrapy
from scrapy_selenium import SeleniumRequest


class ChuteSpider(scrapy.Spider):
    name = 'chute'
    start_urls = ['https://bitchute.com']
    log_path = '/home/phillipdavis/Desktop/comments.json'
    path_path = log_path.replace('json', 'html')

    def start_requests(self):
        yield SeleniumRequest(
            url = self.start_urls[0],
            callback = self.parse_front_page,
            wait_time = 5,
            script = 'window.scrollTo(0, document.body.scrollHeight)'
        )

    def parse_front_page(self, response):
        for video_card in response.selector.css('div.video-card > a.spa::attr(href)').getall():
            yield SeleniumRequest(
                url = f'https://www.bitchute.com{video_card}',
                callback = self.parse_comments,
                script = 'window.scrollTo(0, document.body.scrollHeight)'
            )

    def parse_comments(self, response):
        with open(self.log_path, 'a') as f:
            for comment in response.selector.css('li.comment').getall():
                f.write(f'{comment}\n')

    def parse_video(self, response):
        pass
