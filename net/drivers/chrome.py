# coding: utf-8

import selenium.webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.chrome.webdriver
import webdriver_manager.chrome

import net.drivers.provider


class ChromeWebDriverProvider(net.drivers.provider.WebDriverProvider):
    """
    .. seealso:: https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c
    .. seealso:: https://github.com/heroku/heroku-buildpack-chromedriver
    .. seealso:: https://github.com/heroku/heroku-buildpack-google-chrome
    """

    def __init__(self, chrome_driver_path, chrome_binary_path):
        self.chrome_driver_path = chrome_driver_path
        self.chrome_binary_path = chrome_binary_path

    def get_driver(self):
        options = selenium.webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.binary_location = self.chrome_binary_path

        return selenium.webdriver.Chrome(
            executable_path=self.chrome_driver_path,
            chrome_options=options
        )

    def old_get_driver(self):
        manager = webdriver_manager.chrome.ChromeDriverManager
        executable_path = manager.install()

        chrome_options = selenium.webdriver.chrome.options.Options()
        chrome_options.add_argument("--headless")

        return selenium.webdriver.Chrome(
            executable_path=executable_path,
            chrome_options=chrome_options
        )
