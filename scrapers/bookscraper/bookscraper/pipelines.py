# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from items import BookscraperItem
from spiders.bookspider import BookspiderSpider
class BookscraperPipeline:
    def process_item(self, item: BookscraperItem, spider: BookspiderSpider):
        adapter = ItemAdapter(item)

        # strip extra whicespace
        for field in adapter.field_names():
            if field != "description":
                value = adapter.get(field)
                adapter[field] = value.strip()

        # lowercase
        lowercase_fields =  ["category", "product_type"]
        for field in lowercase_fields:
            value = adapter.get(field)
            adapter[field] = value.lower()

        # remove price units, convert price to float
        price_fields = ["price", "price_excl_tax", "price_incl_tax", "tax"]
        for field in price_fields:
            value = adapter.get(field)
            value = value.replace("£", "")
            adapter[field] = float(value)

        # get number of items availble, strip text
        availability_str = adapter.get("availability")
        availability_str_array = availability_str.split("(")
        if len(availability_str_array) < 2: # none left
            adapter["availability"] = 0
        else:
            availability_value = availability_str_array[1].split(" ")[0]
            adapter["availability"] = int(availability_value)

        # num_reviews as int
        num_reviews_value = adapter.get("num_reviews")
        adapter["num_reviews"] = int(num_reviews_value)

        # stars as int
        stars_value = adapter.get("stars")
        adapter["stars"] = int(stars_value)

        return item