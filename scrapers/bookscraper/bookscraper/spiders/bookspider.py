import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response):
        # get all books from page
        books = response.css("article.product_pod")

        # parse data
        for book in books:
            yield {
                "title": book.css("h3 a::text").get(),
                "price": book.css(".product_price .price_color::text").get(),
                "url": book.css("h3 a").attrib["href"]
            }

        # scroll to next page
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            if not next_page.startswith("catalogue"):
                next_page = "catalogue/" + next_page
            next_page_url = "https://books.toscrape.com/" + next_page
            yield response.follow(next_page_url, callback=self.parse)