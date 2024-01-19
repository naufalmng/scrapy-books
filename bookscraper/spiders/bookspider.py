from random import randint
from urllib.parse import urlencode

import scrapy
from ..items import BookItem


# user_agent_list = get_user_agent()


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com", 'proxy.scrapeops.io']
    start_urls = ["https://books.toscrape.com"]

    # random_user_agent = {
    #     'User-Agent': user_agent_list[randint(0, len(user_agent_list) - 1)]
    # }

    custom_settings = {
        'FEEDS': {
            'booksdata.json': {'format': 'json', 'overwrite': True}
        }
    }

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse)

    def parse(self, response, **kwargs):
        books = response.css('article.product_pod')
        for book in books:
            book_url = book.css('div.image_container a::attr(href)').get()
            if book_url is not None:
                # if 'catalogue' not in book_url:
                #     book_url = 'https://books.toscrape.com/catalogue/' + book_url
                # else:
                #     book_url = 'https://books.toscrape.com/' + book_url
                yield response.follow(url=book_url, callback=self.parse_book_page)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            # if 'catalogue' not in next_page:
            #     next_page = 'https://books.toscrape.com/catalogue/' + next_page
            # else:
            #     next_page = 'https://books.toscrape.com/' + next_page
            # meta = {'proxy': 'http://127.0.0.1:8118'}
            yield response.follow(next_page, callback=self.parse)

    def parse_book_page(self, response):
        book_item = BookItem()
        table_rows = response.css(".table-striped tr")
        book_item.update({
            'url': response.url,
            'category': response.xpath('//*[@id="default"]/div[1]/div/ul/li[3]/a/text()').get(),
            'title': response.css('div.product_main h1::text').get(),
            'description': response.xpath('//*[@id="content_inner"]/article/p/text()').get(),
            'image_url': response.css('div.item.active img::attr(src)').get(),
            'star_rating': response.css('.product_main p.star-rating::attr(class)').get().split(' ')[1],
            'product_type': table_rows[1].css('td ::text').get(),
            'price': response.css('div.product_main p.price_color::text').get(),
            'price_excl_tax': table_rows[2].css('td ::text').get(),
            'price_incl_tax': table_rows[3].css('td ::text').get(),
            'tax': table_rows[4].css('td ::text').get(),
            'availability': table_rows[5].css('td ::text').get(),
            'num_of_reviews': table_rows[6].css('td ::text').get()
        })

        yield book_item
