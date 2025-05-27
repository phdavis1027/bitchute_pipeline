import time

from bs4 import BeautifulSoup

from scrapy import Spider
from scrapy.loader import ItemLoader

from scrapy_selenium import SeleniumRequest

from bitchute.items import TopLevelCommentItem, ChildCommentItem, VideoItem


"""
Phillip Davis
---
This website is a bit of a watering hole for conspiracy theorists and
hardcore bigots of diverse stripes. Part of why I was interested in
scraping this data was to potentially build an ML model to do something like:
- Detect the presence or absence of personally identifying information in the comments
(I have personally found a few instances of people being doxxed on this site)
- Track the dissemination of different conspiracy narratives within different communities
- Track crossover of individual users between communities (the literature suggests that
in-person participants in racist or conspiratorial subcultures tend to bounce around
between groups)

The resources I used were:
- the Scrapy documentation (https://docs.scrapy.org/en/latest/)
- documentation for Scrapy Splash (although I abandoned it because of issues getting the page to fully render)
https://github.com/scrapy-plugins/scrapy-splash
- the documentation for Selenium-Scrapy (which I used because it just worked)
https://github.com/clemfromspace/scrapy-selenium
- a little bit of documentation from BeautifulSoup
https://beautiful-soup-4.readthedocs.io/en/latest/

I like this project for a couple of reasons:
1. It forced me to learn a lot about Middleware, specifically Javascript rendering APIs, although that
isn't necessarily visible in the final product.
2. It's slow for safety, but left to its own devices for long enough I'm fairly confident it could keep going
for a very long time, indefinitely if I had my way. I stopped at around 2000 items arbitrarily.
I then split the pipeline into two files just to prove the design could work that way.
3. I struggled for a little bit to get the right relationship between child comments and top-level comments,
but the resulting structure for comment records is satisfying to me.

There are still a few more directions I want to take this, and hopefully will, either the next time
I have spare time or as this class progresses:
1. Index these in a database -- I'm looking at Mongo but it doesn't run on my version of Ubuntu.
2. Scrape channel information, which should be fairly trivial if quite slow.

"""

class ChuteSpider(Spider):
    name = 'chute'
    start_urls = ['https://bitchute.com']
    scroll_script = """
        for (let _ = 0; _ < 20; ++_) {
           await new Promise(r => setTimeout(r, 500));
           window.scrollTo(0, document.body.scrollHeight)
        }
    """

    def start_requests(self):
        yield SeleniumRequest(
            url = self.start_urls[0],
            callback = self.parse_front_page,
            wait_time = 5,
            script = self.scroll_script
        )

    def parse_front_page(self, response):
        front_page = BeautifulSoup(response.body)
        for video_card in front_page.select('div.video-card > a.spa'):
            yield SeleniumRequest(
                url = f'https://www.bitchute.com{video_card.get("href")}',
                callback = self.full_scrape_video,
                script = self.scroll_script
            )

    def full_scrape_video(self, response):
        video_page_soup = BeautifulSoup(response.body)
        video_title = video_page_soup.select_one('h1#video-title').get_text().strip()
        yield from self.scrape_comments(response, video_page_soup, video_title)
        yield self.scrape_video(response, video_page_soup, video_title)
        yield from self.follow_recommended_videos(response, video_page_soup)

    """ COMMENTS """

    def scrape_comments(self, response, video_page_soup, video):
        if video:
            for comment in video_page_soup.select('li.comment'):
                parsed_comment = self.parse_comment(comment, response, video)
                if parsed_comment:
                    yield parsed_comment

    def parse_comment(self, comment_soup, response, video):
        if not video: ## Funnily enough, some of these videos are content-restricted in certain locations
            return None
        if 'comment' in comment_soup.parent.parent['class']:
            return None ## it's a child comment
        if 'comment' in comment_soup.parent['class']:
            return None

        loader = ItemLoader(item = TopLevelCommentItem(), response = response)

        loader.add_value('video', video)

        content = comment_soup.select_one('div.content').get_text().strip()
        loader.add_value('content', content)

        timestamp = comment_soup.find('time').find_next().get('data-original')
        loader.add_value('timestamp', timestamp)

        author_id = comment_soup.select_one('div.profile-picture').get('data-user-id')
        loader.add_value('author_id', author_id)

        author_username = comment_soup.select_one('div.comment-header > span.name').get_text().strip()
        loader.add_value('author_username', author_username)

        comment_id = comment_soup.get('data-id')
        loader.add_value('comment_id', comment_id)

        likes = comment_soup.select_one('button.action.upvote > span.vote-count').get_text().strip()
        loader.add_value('likes', likes)

        dislikes = comment_soup.select_one('button.action.downvote > span.vote-count').get_text().strip()
        loader.add_value('dislikes', dislikes)

        replies = []
        for child_comment in comment_soup.select('ul.child-comments > li.comment'):
            replies.append(self.parse_child_comment(child_comment, comment_id, response, video))
        loader.add_value('replies', replies)

        return loader.load_item()

    def parse_child_comment(self, comment_soup, parent_comment_id, response, video):
        loader = ItemLoader(item = ChildCommentItem(), response = response)

        loader.add_value('video', video)
        loader.add_value('parent_comment_id', parent_comment_id)

        content = comment_soup.select_one('div.content').get_text().strip()
        loader.add_value('content', content)

        timestamp = comment_soup.find('time').find_next().get('data-original')
        loader.add_value('timestamp', timestamp)

        author_id = comment_soup.select_one('div.profile-picture').get('data-user-id')
        loader.add_value('author_id', author_id)

        author_username = comment_soup.select_one('div.comment-header > span.name').get_text().strip()
        loader.add_value('author_username', author_username)

        comment_id = comment_soup.get('data-id')
        loader.add_value('comment_id', comment_id)

        likes = comment_soup.select_one('button.action.upvote > span.vote-count').get_text().strip()
        loader.add_value('likes', likes)

        dislikes = comment_soup.select_one('button.action.downvote > span.vote-count').get_text().strip()
        loader.add_value('dislikes', dislikes)

        return dict(loader.load_item())

    def has_child_comments(self, comment_soup):
        return len(comment_soup.select('ul.child-comments > li.comment')) == 0

    """ FOLLOWING """

    def follow_recommended_videos(self, response, video_page_soup):
        for video_card in video_page_soup.select('div.video-card > a.spa'):
            href = video_card.get('href')
            url = f'https://www.bitchute.com{video_card.get("href")}'
            yield SeleniumRequest(
                url = url,
                callback = self.full_scrape_video,
                script = self.scroll_script
            )

    """ VIDEO """

    def scrape_video(self, response, video_page_soup, video):
        if not video:
            return None

        loader = ItemLoader(item = VideoItem(), response = response)

        loader.add_value('title', video)
        loader.add_value('url', response.url)

        description = video_page_soup.select_one('#video-description').get_text()
        loader.add_value('description', description)

        for tr in video_page_soup.select('table.video-detail-list > tbody > tr'):
            tds = tr.find('td')
            if 'category' in tds.find_next().get_text().lower():
                category = tds.find_next().select_one('a.spa').get_text()
                loader.add_value('category', category)
            if 'sensitivity' in tds.find_next().get_text().lower():
                sensitivty = tds.find_next().select_one('a.spa').get_text()
                loader.add_value('sensitivity', sensitivity)

        timestamp = video_page_soup.select_one('div.col-xs-12 > div.video-publish-date').get_text()
        loader.add_value('timestamp', timestamp)

        video_statistics = video_page_soup.select_one('div.video-statistics')
        views = video_statistics.select_one('span#video-view-count').get_text()
        loader.add_value('views', views)

        likes = video_statistics.select_one('#video-like').get_text()
        loader.add_value('likes', likes)

        dislikes = video_statistics.select_one('#video-dislike').get_text()
        loader.add_value('dislikes', dislikes)

        channel = video_page_soup.select_one('div.channel-banner > div.details > p.name > a.spa').get_text()
        loader.add_value('channel', channel)

        self.logger.debug(f'[LOADED ITEM] [{type(loader.load_item())}]')

        return loader.load_item()
