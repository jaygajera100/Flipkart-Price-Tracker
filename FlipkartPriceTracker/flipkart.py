import time
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from pathlib import Path
import json
import qrcode
import shutil
from my_config import (
    get_web_driver_options,
    get_chrome_web_driver,
    set_ignore_certificate_error,
    set_browser_as_incognito,
    set_automation_as_head_less,
    get_soup_data,
    NAME,
    CURRENCY,
    BASE_URL,
    DIRECTORY
)


class GenerateReport:
    def __init__(self, file_name, base_link, currency, data):
        self.data = data
        self.file_name = file_name
        self.base_link = base_link
        self.currency = currency
        report = {
            'title': self.file_name,
            'date': self.get_now(),
            'currency': self.currency,
            'base_link': self.base_link,
            'products': self.data
        }
        print("Creating report...")
        with open('report.json', 'w') as f:
            json.dump(report, f)

        print("Done...")

    @staticmethod
    def get_now():
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")


class Flipkart_API:
    def __init__(self, search_term, currency, base_url):
        self.base_url = base_url
        self.search_term = search_term
        self.currency = currency
        options = get_web_driver_options()
        set_browser_as_incognito(options)
        # set_automation_as_head_less(options)
        set_ignore_certificate_error(options)
        self.driver = get_chrome_web_driver(options)
        self.soup = get_soup_data(self.base_url)

    def run(self):
        print("Start Scripting...")
        print(f'Looking for {self.search_term} items....')
        links = self.get_products_links()
        if not links:
            print('stopped script.....')
            return
        print(f"Got {len(links)} links to products...")
        print("Getting info about products...")
        products = self.get_products_info(links)
        print(f"Got info about {len(products)} products...")
        self.driver.quit()
        return products

    def get_products_links(self):
        self.driver.get(self.base_url)
        element = self.driver.find_element_by_name('q')
        element.send_keys(self.search_term)
        element.send_keys(Keys.ENTER)
        time.sleep(2)
        links = []

        for page in range(1, 2):  # Page range you want to extract
            temp_link = f'{self.base_url}/search?q={self.search_term}&page={page}'
            self.driver.get(temp_link)
            self.soup = get_soup_data(temp_link)
            time.sleep(1)
            result_list = self.soup.findAll('a', class_='s1Q9rs')
            try:
                # From each page you want to extract link
                for link in result_list[:]:
                    lin = link.get('href')
                    links.append(lin)
            except Exception as e:
                print("Link didn't catch")
                print(e)
        return links

    def get_products_info(self, links):
        asins = self.get_asins(links)
        product_id = self.get_product_id(asins)
        products = []
        i = 0
        for asin in asins:
            product = self.get_single_product_info(asin, product_id[i])
            if product:
                products.append(product)
            i += 1
        return products

    def get_single_product_info(self, asin, product_id):
        print(f"Product {product_id} - Getting Data... ")
        product_short_url = self.shorten_url(asin, product_id)
        self.driver.get(product_short_url)
        # get the soup data from single product link
        self.soup = get_soup_data(product_short_url)
        time.sleep(1)
        title = self.get_title()
        seller = self.get_seller()
        price = self.get_price()
        time.sleep(1)
        if title and seller and price:
            product_info = {
                'product_id': product_id,
                'url': product_short_url,
                'title': title,
                'seller': seller,
                'price': price
            }
            return product_info
        return None

    def get_title(self):
        try:
            return self.soup.find('span', class_='B_NuCI').text
        except Exception as e:
            print("Didn't get the title !!")
            print(e)
            return None

    def get_seller(self):
        try:
            dump = self.soup.find(id='sellerName').find(
                'span').find('span').text
            return dump
        except Exception as e:
            print("Didn't get the seller")
            print(e)
            return None

    def get_price(self):
        price = None
        try:
            price = self.soup.find('div', class_="_30jeq3 _16Jk6d").text
            price = self.convert_price(price)
            return price
        except Exception as e:
            print("You didn't Catch the Price")
            return None

    def shorten_url(self, asin, product_id):
        return self.base_url + asin

    def get_asins(self, links):
        # Catch link As you want-1
        return [self.get_asin(link) for link in links]

    @staticmethod
    def get_asin(product_link):
        return product_link[:product_link.find('?')]

    def get_product_id(self, product_links):
        # Catch link as you want-2
        return [self.get_id(link) for link in product_links]

    @staticmethod
    def get_id(product_id):
        return product_id[product_id.find('/p/') + 3:]

    def convert_price(self, price):
        price = price.split(self.currency)[1]
        try:
            price = price.split(
                ',')[0] + price.split(',')[1] + price.split(',')[2]
        except:
            Exception()
        try:
            price = price.split(',')[0] + price.split(',')[1]
        except:
            Exception()
        return float(price)


if __name__ == "__main__":
    am = Flipkart_API(NAME, CURRENCY, BASE_URL)
    data = am.run()
    GenerateReport(NAME, BASE_URL, CURRENCY, data)
