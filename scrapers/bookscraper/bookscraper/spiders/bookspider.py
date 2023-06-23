import scrapy
from scrapy.http import Response

from ..items import BookscraperItem

STAR_RATINGS = {
    "One" : 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

class BookspiderSpider(scrapy.Spider):
    """
    Simple web spider to scrapy book data.
    """
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response: Response) -> dict[str, str]:
        """
        Top-level parse function to extract data from each book ion page.

        :param: response - HTTP response object of book page.
        :dtype: Response
        :return - scraped book data
        :rtype: dict[str, str,]
        """
        # get all books from page
        books = response.css("article.product_pod")

        # parse data from all books on page
        for book in books:
            # navigate to full page
            book_relative_url = book.css("h3 a::attr(href)").get()

            if not book_relative_url.startswith("catalogue/"):
                book_relative_url = "catalogue/" + book_relative_url
            full_book_url = "https://books.toscrape.com/" + book_relative_url
            yield response.follow(full_book_url, callback=self.parse_full_book_page)

        # scroll to next page
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            if not next_page.startswith("catalogue"):
                next_page = "catalogue/" + next_page
            next_page_url = "https://books.toscrape.com/" + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_full_book_page(self, response: Response) -> dict[str, str]:
        """
        Parse data from full book page.

        :param: response - HTTP response object of full book page.
        :dtype: Response
        :return - scraped book data
        :rtype: dict[str, str,]
        """
        # Get data from table
        table_rows = response.css(".table-striped tr")

        book_item = BookscraperItem()

        book_item["url"] = response.url,
        book_item["title"] = response.css(".product_main h1::text").get()
        book_item["upc"] = table_rows[0].css("td::text").get()
        book_item["product_type"] = table_rows[1].css("td::text").get()
        book_item["price_excl_tax"] = table_rows[2].css("td::text").get()
        book_item["price_incl_tax"] = table_rows[3].css("td::text").get()
        book_item["tax"] = table_rows[4].css("td::text").get()
        book_item["availability"] = table_rows[5].css("td::text").get()
        book_item["num_reviews"] = table_rows[6].css("td::text").get()
        book_item["stars"] = STAR_RATINGS[
            response.css(".star-rating").attrib["class"].split(" ")[-1]
        ]
        book_item["category"] = response.css("ul.breadcrumb li a ::text")[-1].get()
        book_item["description"] = response.xpath(
            "//div[@id='product_description']//following-sibling::p/text()").get()
        book_item["price"] = response.css("p.price_color::text").get()

        yield book_item