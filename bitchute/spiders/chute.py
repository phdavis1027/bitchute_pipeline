import time

from bs4 import BeautifulSoup

from scrapy import Spider
from scrapy.loader import ItemLoader

from scrapy_selenium import SeleniumRequest

from bitchute.items import TopLevelCommentItem, ChildCommentItem


class ChuteSpider(Spider):
    name = 'chute'
    start_urls = ['https://bitchute.com']

    def start_requests(self):
        yield SeleniumRequest(
            url = self.start_urls[0],
            callback = self.parse_front_page,
            wait_time = 5,
            script = 'window.scrollTo(0, document.body.scrollHeight)'
        )

    def parse_front_page(self, response):
        front_page = BeautifulSoup(response.body)
        for video_card in front_page.select('div.video-card > a.spa'):
            yield SeleniumRequest(
                url = f'https://www.bitchute.com{video_card.get("href")}',
                callback = self.full_scrape_video,
                script = 'window.scrollTo(0, document.body.scrollHeight)'
            )

    def full_scrape_video(self, response):
        video_page_soup = BeautifulSoup(response.body)
        yield from self.scrape_comments(response, video_page_soup)
        # yield from self.scrape_video(response, video_page_soup)
        # yield from self.follow_recommended_videos(response, video_page_soup)

    """ COMMENTS """

    def scrape_comments(self, response, video_page_soup):
        video = video_page_soup.select_one('h1#video-title').get_text().strip()
        if video:
            for comment in video_page_soup.select('li.comment'):
                parsed_comment = self.parse_comment(comment, response, video)
                if parsed_comment:
                    yield parsed_comment

    def parse_comment(self, comment_soup, response, video):
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

    def construct_comment_item(self, comment_soup):
        pass

    """ FOLLOWING """

    def follow_recommended_videos(self, response, video_page_soup):
        pass

    """ VIDEO """

    def scrape_video(self, response, video_page_soup):
        pass

    def parse_video(self, response):
        pass

