# coding: utf-8

import selenium.webdriver
import selenium.webdriver.firefox.firefox_binary
import selenium.webdriver.firefox.options
import webdriver_manager.firefox

import net.drivers.provider


class FirefoxWebDriverProvider(net.drivers.provider.WebDriverProvider):

    def get_driver_manager_class(self):
        return webdriver_manager.firefox.GeckoDriverManager

    def get_driver(self, executable_path):
        firefox_options = selenium.webdriver.firefox.options.Options()
        firefox_options.headless = True

        firefox_profile = selenium.webdriver.firefox.options.FirefoxProfile()
        firefox_profile.set_preference("dom.disable_beforeunload", True)

        return selenium.webdriver.Firefox(
            executable_path=executable_path,
            firefox_options=firefox_options,
            firefox_profile=firefox_profile
        )
