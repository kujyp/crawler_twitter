from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from crawler.driver import console, download
from crawler.driver.configs import SELENIUM_TIME_TO_WAIT_IN_SECONDS
from crawler.driver.download import download_chromedriver


def open_browser():
    chromedriver_path = download_chromedriver()
    options = Options()
    options.headless = True
    driver = WebDriver(chromedriver_path, options=options)
    driver.implicitly_wait(SELENIUM_TIME_TO_WAIT_IN_SECONDS)

    return driver
