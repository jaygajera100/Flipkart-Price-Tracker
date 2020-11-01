from selenium import webdriver
from bs4 import BeautifulSoup
import requests

DIRECTORY = 'reports'
NAME = 'iphone'
CURRENCY = '₹'

BASE_URL = "https://www.flipkart.com"


def get_soup_data(BASE_URL):
    respond = requests.get(BASE_URL)
    return BeautifulSoup(respond.content, 'html.parser')


def get_chrome_web_driver(options):
    return webdriver.Chrome("./chromedriver", chrome_options=options)


def get_web_driver_options():
    return webdriver.ChromeOptions()


def set_ignore_certificate_error(options):
    options.add_argument('--ignore-certificate-errors')


def set_browser_as_incognito(options):
    options.add_argument('--incognito')


def set_automation_as_head_less(options):
    options.add_argument('--headless')
