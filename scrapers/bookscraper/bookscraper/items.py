# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

def serialize_price(value: str) -> str:
    """
    Serialize price w/ proper pound symbol.

    :param: value - unserialized price
    :dtype: str
    :return: serialized price
    :rtype: str
    """
    return f"£ {value}"

class BookscraperItem(scrapy.Item):
    """
    Scraped book information
    """
    url = scrapy.Field()
    title = scrapy.Field()
    upc = scrapy.Field()
    product_type = scrapy.Field()
    price_excl_tax = scrapy.Field()
    price_incl_tax = scrapy.Field()
    tax = scrapy.Field()
    availability = scrapy.Field()
    num_reviews = scrapy.Field()
    stars = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()

