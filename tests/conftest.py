import atexit

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from crawler.driver import open_browser


@pytest.fixture
def driver() -> WebDriver:
    driver = open_browser()
    atexit.register(lambda: driver.quit())

    return driver
