# coding: utf-8

class WebDriverProvider(object):

    def get_driver(self):
        raise NotImplementedError("subclasses must override this method")

    def provide_driver(self):
        return self.get_driver()
