# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

digit_regex = re.compile(r"\d+")


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        ## Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field in field_names:
            if field != 'description':
                adapter[field] = adapter[field].strip()

        ## Category & Product Type --> switch to lowercase
        lowercase_keys = ['category', 'product_type']
        for key in lowercase_keys:
            adapter[key] = adapter[key].lower()

        ## Clean price (Price --> to float)
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for key in price_keys:
            adapter[key] = float(adapter[key].replace('£', ''))

        ## Availability --> extract the number only
        adapter['availability'] = int(digit_regex.findall(adapter['availability'])[0])

        ## num_of_reviews --> to int number
        adapter['num_of_reviews'] = int(adapter['num_of_reviews'])

        ## image_url --> to absolute ref
        base_url = 'http://books.toscrape.com/'
        adapter['image_url'] = base_url + adapter['image_url'].replace('../../', '')

        ## stars text --> to number
        star_text = adapter['star_rating'].lower()
        star_num = -1
        if star_text == 'zero':
            star_num = 0
        elif star_text == 'one':
            star_num = 1
        elif star_text == 'two':
            star_num = 2
        elif star_text == 'three':
            star_num = 3
        elif star_text == 'four':
            star_num = 4
        elif star_text == 'five':
            star_num = 5
        adapter['star_rating'] = star_num

        return item


import mysql.connector


class SaveToMySQLPipeline:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        # Create 'books' database if it doesn't exist
        self.cur.execute("CREATE DATABASE IF NOT EXISTS books")
        self.cur.execute("USE books")

        ## Create table
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url VARCHAR(255),
                title VARCHAR(255),
                category VARCHAR(255),
                product_type VARCHAR(255),
                star_rating INT,
                price DECIMAL,
                price_excl_tax DECIMAL,
                price_incl_tax DECIMAL,
                tax DECIMAL,
                availability INT,
                num_of_reviews INT,
                image_url VARCHAR(255),
                description TEXT)
            """
        )

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        ## Define insert statement
        self.cur.execute(
            """
            insert into books (
                url,
                title, 
                category, 
                product_type, 
                star_rating, 
                price, 
                price_excl_tax, 
                price_incl_tax, 
                tax, 
                availability, 
                num_of_reviews, 
                image_url, 
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
            )
            """, (
                item['url'],
                item['title'],
                item['category'],
                item['product_type'],
                item['star_rating'],
                item['price'],
                item['price_excl_tax'],
                item['price_incl_tax'],
                item['tax'],
                item['availability'],
                item['num_of_reviews'],
                item['image_url'],
                item['description']
            )
        )
        self.connection.commit()
        return item
