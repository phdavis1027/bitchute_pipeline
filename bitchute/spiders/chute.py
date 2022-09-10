import scrapy
import scrapy_splash
from scrapy_splash import SplashRequest


class ChuteSpider(scrapy.Spider):
    name = 'chute'
    allowed_domains = ['bitchute.com']
    start_urls = ['https://bitchute.com']
    script = """
        function main(splash)
            local num_scrolls = 20
            local scroll_delay = 1.0

            local scroll_to = splash:jsfunc("window.scrollTo")
            local get_body_height = splash:jsfunc(
                "function() {return document.body.scrollHeight;}"
            )
            splash:set_viewport_full()
            assert(splash:wait(0.5))
            assert(splash:go(splash.args.url))
            splash:wait(splash.args.wait)

            for _ = 1, num_scrolls do
                print("Scrolling...")
                scroll_to(0, 500)
                splash:wait(scroll_delay)
            end
            return splash:html()
        end
    """

    def start_requests(self):
        yield SplashRequest(
            self.start_urls[0],
            self.parse_front_page,
            args = {
                'wait': 5,
                'render_all': 1,
            },
            endpoint = 'render.html'
        )

    def parse_front_page(self, response):
        for video_card in response.css('div.video-card > a.spa::attr(href)').getall():
            yield SplashRequest(
                response.urljoin(video_card),
                self._parse_vid,
                cache_args =['lua_source'],
                args = {
                    'wait': 2,
                    'html': 1,
                    'png' : 1,
                    'render_all': 1,
                    'width': 1280,
                    'lua_source': self.script,
                    'height':1024
                },
                endpoint = 'execute'
            )

    def _parse_vid(self, response):
        self.logger.debug(response.css('div.video-comments').get())
        yield self.parse_comments(response)
        yield self.parse_video(response)

    def parse_comments(self, response):
        for title in response.css('h1#video-title::text').getall():
            self.logger.debug(title)

    def parse_video(self, response):
        pass
