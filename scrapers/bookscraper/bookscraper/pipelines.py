# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import mysql.connector
from itemadapter import ItemAdapter

from .items import BookscraperItem
from .spiders.bookspider import BookspiderSpider
class BookscraperPipeline:
    """
    Pipeline to scrape and save books from books.toscrape.com
    """
    def process_item(self, item: BookscraperItem, spider: BookspiderSpider) -> BookscraperItem:
        """
        Processes a book scraper item usind spider.

        :param: item - Item containing scraped book information
        :dtype: BookscraperItem
        :param: spider - Spider object that scraped the book information
        :dtype: BookspiderSpider
        :return: post-processed book information
        :rtype: BookscraperItem
        """
        adapter = ItemAdapter(item)

        # strip extra whicespace
        for field in adapter.field_names():
            if field not in ["description", "stars"]:
                value = adapter.get(field)
                if type(value) == tuple:
                    value = value[0]
                adapter[field] = value.strip()

        # lowercase
        lowercase_fields = ["category", "product_type"]
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

    class MySQLPipeline:

        def __init__(self) -> None:
            self.conn = mysql.connector.connect(
                host = "localhost",
                user = "root",
                password = "",
                database = "books"
            )

            self.cur = self.conn.cursor()

            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS books(
                id int NOT NULL auto_increment, 
                url VARCHAR(255),
                title text,
                upc VARCHAR(255),
                product_type VARCHAR(255),
                price_excl_tax DECIMAL,
                price_incl_tax DECIMAL,
                tax DECIMAL,
                price DECIMAL,
                availability INTEGER,
                num_reviews INTEGER,
                stars INTEGER,
                category VARCHAR(255),
                description text,
                PRIMARY KEY (id)
            )
            """)

    def process_item(self, item: BookscraperItem, spider: BookspiderSpider) -> BookscraperItem:
        """
        Processes a book scraper item usind spider and inserts into mysql database.

        :param: item - Item containing scraped book information
        :dtype: BookscraperItem
        :param: spider - Spider object that scraped the book information
        :dtype: BookspiderSpider
        :return: post-processed book information
        :rtype: BookscraperItem
        """
        ## Define insert statement
        self.cur.execute(""" insert into books (
            url,
            title,
            upc,
            product_type,
            price_excl_tax,
            price_incl_tax,
            tax,
            price,
            availability,
            num_reviews,
            stars,
            category,
            description
            ) values (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
                )""", (
            item["url"],
            item["title"],
            item["upc"],
            item["product_type"],
            item["price_excl_tax"],
            item["price_incl_tax"],
            item["tax"],
            item["price"],
            item["availability"],
            item["num_reviews"],
            item["stars"],
            item["category"],
            str(item["description"][0])
        ))

        # Execute insert of data into database
        self.conn.commit()
        return item

    def close_spider(self, spider: BookspiderSpider) -> None:
        """
        Disconnect from MySQL database after scraping is finished.

        :param: spider - spider that scrapes books
        :dtype: BookspiderSpider
        :return: None
        :rtype: NoneType
        """
        self.curr.close()
        self.conn.close()