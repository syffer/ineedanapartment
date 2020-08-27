# coding: utf-8

import urllib.parse
import selenium.webdriver
import selenium.webdriver.common.by
import selenium.webdriver.common.keys
import selenium.webdriver.common.desired_capabilities
import selenium.webdriver.chrome.options
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.firefox.firefox_binary
import selenium.webdriver.firefox.options
import selenium.webdriver.support.ui
import selenium.webdriver.support.expected_conditions
import webdriver_manager.firefox
import webdriver_manager.chrome
import psutil


class WebDriverProvider(object):
    def get_driver_manager_class(self):
        raise NotImplementedError("subclasses must override this method")

    def get_executable_path(self):
        driver_manager_class = self.get_driver_manager_class()
        driver_manager = driver_manager_class()
        return driver_manager.install()

    def get_driver(self, executable_path):
        raise NotImplementedError("subclasses must override this method")

    def provide_driver(self):
        executable_path = self.get_executable_path()
        return self.get_driver(executable_path)


class FirefoxWebDriverProvider(WebDriverProvider):

    def get_driver_manager_class(self):
        return webdriver_manager.firefox.GeckoDriverManager

    def get_driver(self, executable_path):
        firefox_options = selenium.webdriver.firefox.options.Options()
        # firefox_options.headless = True

        firefox_profile = selenium.webdriver.firefox.options.FirefoxProfile()
        firefox_profile.set_preference("dom.disable_beforeunload", True)

        return selenium.webdriver.Firefox(
            executable_path=executable_path,
            firefox_options=firefox_options,
            firefox_profile=firefox_profile
        )


class ChromeBrowwserProvider(WebDriverProvider):

    def get_driver_manager_class(self):
        return webdriver_manager.chrome.ChromeDriverManager

    def get_driver(self, executable_path):
        chrome_options = selenium.webdriver.chrome.options.Options()
        chrome_options.add_argument("--headless")

        return selenium.webdriver.Chrome(
            executable_path=executable_path,
            chrome_options=chrome_options
        )


class OperaWebDriverProvider(WebDriverProvider):

    def get_driver_manager_class(self):
        import webdriver_manager.opera
        return webdriver_manager.opera.OperaDriverManager

    def get_driver(self, executable_path):
        import selenium.webdriver.opera

        return selenium.webdriver.Opera(
            executable_path=executable_path
        )


class EdgeWebDriverProvider(WebDriverProvider):

    def get_driver_manager_class(self):
        import webdriver_manager.microsoft
        return webdriver_manager.microsoft.EdgeChromiumDriverManager

    def get_driver(self, executable_path):
        return selenium.webdriver.Ie(
            executable_path=executable_path
        )


class Browser(object):

    def __init__(self):
        browser_provider = FirefoxWebDriverProvider()
        self.browser = browser_provider.provide_driver()

    def load_page(self, url, params=None):
        print("load page {} {}".format(url, params))
        params = params or {}
        params = {key: value for key, value in params.items() if value is not None}

        formatted_url = "{url}?{params}".format(url=url, params=urllib.parse.urlencode(params))
        self.browser.get(url=formatted_url)

    def get_page(self):
        return self.browser.page_source

    def wait_for(self, css_selector, timeout):
        print("wait for {}".format(css_selector))
        selenium.webdriver.support.ui.WebDriverWait(self.browser, timeout).until(
            selenium.webdriver.support.expected_conditions.presence_of_element_located(
                (selenium.webdriver.common.by.By.CSS_SELECTOR, css_selector))
        )

    def click_on_element(self, css_selector):
        print("click on {}".format(css_selector))
        self.browser.find_element_by_css_selector(css_selector).click()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser.service.process:
            self.browser.quit()
            self.browser = None
        return
        # https://stackoverflow.com/questions/46619679/in-python-how-to-check-if-selenium-webdriver-has-quit-or-not/46620600#46620600
        """
        driver_process = psutil.Process(self.browser.service.process.pid)
        if driver_process.is_running():
            firefox_process = driver_process.children()
            if firefox_process:
                if not firefox_process[0].is_running():
                    firefox_process[0].kill()
        """
