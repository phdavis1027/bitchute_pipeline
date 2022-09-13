# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class TopLevelCommentItem(Item):
    comment_id = Field()
    author_id = Field()
    author_username = Field()
    timestamp = Field()
    content = Field()
    replies = Field()
    video = Field()
    likes = Field()
    dislikes = Field()

class ChildCommentItem(Item):
    comment_id = Field()
    author_id = Field()
    author_username = Field()
    timestamp = Field()
    content = Field()
    parent_comment_id = Field()
    video = Field()
    likes = Field()
    dislikes = Field()

class VideoItem(Item):
    title = Field()
    url = Field()
    description = Field()
    channel = Field()
    timestamp = Field()
    description = Field()
    sensitivity = Field()
    recommendeds = Field()
    views = Field()
    likes = Field()
    dislikes = Field()
