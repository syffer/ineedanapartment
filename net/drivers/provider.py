# coding: utf-8

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
