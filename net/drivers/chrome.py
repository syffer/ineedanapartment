# coding: utf-8

import selenium.webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.chrome.webdriver
import webdriver_manager.chrome

import net.drivers.provider


class ChromeWebDriverProvider(net.drivers.provider.WebDriverProvider):

    def get_driver_manager_class(self):
        return webdriver_manager.chrome.ChromeDriverManager

    def get_driver(self, executable_path):
        chrome_options = selenium.webdriver.chrome.options.Options()
        chrome_options.add_argument("--headless")

        return selenium.webdriver.Chrome(
            executable_path=executable_path,
            chrome_options=chrome_options
        )
