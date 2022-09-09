import scrapy
import scrapy_splash
from scrapy_splash import SplashRequest


class ChuteSpider(scrapy.Spider):
    name = 'chute'
    allowed_domains = ['bitchute.com']
    start_urls = ['https://bitchute.com']

    def start_requests(self):
        yield SplashRequest(
            self.start_urls[0],
            self.parse_front_page,
            args = {
                'wait': 0.5
            },
            endpoint = 'render.html'
        )

    def parse_front_page(self, response):
        self.logger.debug(response.body)

    def _parse_vid(self, response):
        yield self.parse_comments(response)
        yield self.parse_video(response)

    def parse_comments(self, response):
        for comment in response.css('li.comment').getall():
            self.logger.debug(f"BIG COMMENT HERE: [{comment}]")

    def parse_video(self, response):
        pass
