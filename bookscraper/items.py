# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


def serialize_price(value):
    return f'£ {str(value)}'


class BookItem(scrapy.Item):
    url = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    image_url = scrapy.Field()
    star_rating = scrapy.Field()
    product_type = scrapy.Field()
    price = scrapy.Field()
    price_excl_tax = scrapy.Field()
    price_incl_tax = scrapy.Field()
    tax = scrapy.Field()
    availability = scrapy.Field()
    num_of_reviews = scrapy.Field()
