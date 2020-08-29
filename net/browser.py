# coding: utf-8

import urllib.parse
import selenium.webdriver.common.by
import selenium.webdriver.common.keys
import selenium.webdriver.common.desired_capabilities
import selenium.webdriver
import selenium.webdriver.support.ui
import selenium.webdriver.support.expected_conditions


class Browser(object):

    def __init__(self, driver_provider):
        self.browser = driver_provider.provide_driver()

    def load_page(self, url, params=None):
        params = params or {}
        params = {key: value for key, value in params.items() if value is not None}

        formatted_url = "{url}?{params}".format(url=url, params=urllib.parse.urlencode(params))
        self.browser.get(url=formatted_url)

    def get_page(self):
        return self.browser.page_source

    def wait_for(self, css_selector, timeout):
        selenium.webdriver.support.ui.WebDriverWait(self.browser, timeout).until(
            selenium.webdriver.support.expected_conditions.presence_of_element_located(
                (selenium.webdriver.common.by.By.CSS_SELECTOR, css_selector))
        )

    def click_on_element(self, css_selector):
        self.browser.find_element_by_css_selector(css_selector).click()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # https://stackoverflow.com/questions/46619679/in-python-how-to-check-if-selenium-webdriver-has-quit-or-not/46620600#46620600
        """
        import psutil
        driver_process = psutil.Process(self.browser.service.process.pid)
        if driver_process.is_running():
            firefox_process = driver_process.children()
            if firefox_process:
                if not firefox_process[0].is_running():
                    firefox_process[0].kill()
        """
        if self.browser.service.process:
            self.browser.quit()
            self.browser = None
