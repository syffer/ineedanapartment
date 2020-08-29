# coding: utf-8

import selenium.webdriver
import selenium.webdriver.firefox.firefox_binary
import selenium.webdriver.firefox.options
import webdriver_manager.firefox

import net.drivers.provider


class FirefoxWebDriverProviderTest(net.drivers.provider.WebDriverProvider):

    def get_driver(self):
        manager = webdriver_manager.firefox.GeckoDriverManager()
        executable_path = manager.install()

        firefox_options = selenium.webdriver.firefox.options.Options()
        firefox_options.headless = True

        firefox_profile = selenium.webdriver.firefox.options.FirefoxProfile()
        firefox_profile.set_preference("dom.disable_beforeunload", True)

        return selenium.webdriver.Firefox(
            executable_path=executable_path,
            firefox_options=firefox_options,
            firefox_profile=firefox_profile
        )


class FirefoxWebDriverProvider(net.drivers.provider.WebDriverProvider):

    def __init__(self, firefox_binary_path, firefox_gecko_path):
        super().__init__()
        self.firefox_binary_path = firefox_binary_path

        if not firefox_gecko_path:
            manager = webdriver_manager.firefox.GeckoDriverManager()
            firefox_gecko_path = manager.install()

        self.firefox_gecko_path = firefox_gecko_path

    def get_driver(self):
        firefox_options = selenium.webdriver.firefox.options.Options()
        firefox_options.headless = True

        firefox_profile = selenium.webdriver.firefox.options.FirefoxProfile()
        firefox_profile.set_preference("dom.disable_beforeunload", True)

        firefox_binary = None
        if self.firefox_binary_path:
            firefox_binary = selenium.webdriver.firefox.options.FirefoxBinary(self.firefox_binary_path)

        return selenium.webdriver.Firefox(
            executable_path=self.firefox_gecko_path,
            firefox_binary=firefox_binary,
            firefox_options=firefox_options,
            firefox_profile=firefox_profile
        )
