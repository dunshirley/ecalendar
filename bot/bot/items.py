# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ActivityItem(Item):
    title = Field()
    link = Field()
    content = Field()
    start_time = Field()
    end_time = Field()
    city = Field()
