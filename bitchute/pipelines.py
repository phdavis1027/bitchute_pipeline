# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
from bitchute.items import TopLevelCommentItem, VideoItem, ChildCommentItem

class BitchutePipeline:

    def open_spider(self, spider):
        self.comments_file = open('comments.json', 'w+')
        self.videos_file = open('videos.json', 'w+')

    def close_spider(self, spider):
        self.comments_file.close()
        self.videos_file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + '\n'
        if isinstance(item, TopLevelCommentItem):
            self.comments_file.write(line)
        elif isinstance(item, VideoItem):
            self.videos_file.write(line)
        return item
