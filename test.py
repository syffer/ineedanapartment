# coding: utf-8

import selenium.webdriver
import selenium.webdriver.common.keys
import selenium.webdriver.firefox.firefox_binary
import selenium.webdriver.common.desired_capabilities
import selenium.webdriver.firefox.options
import webdriver_manager.firefox
import webdriver_manager.chrome
from webdriver_manager.utils import ChromeType

gecko_driver_manager = webdriver_manager.firefox.GeckoDriverManager()
result = gecko_driver_manager.install()
print(result)

firefox_options = selenium.webdriver.firefox.options.Options()
firefox_options.headless = True

with selenium.webdriver.Firefox(executable_path=result, firefox_options=firefox_options) as browser:
    browser.get("https://google.fr")
    print(browser.title)
