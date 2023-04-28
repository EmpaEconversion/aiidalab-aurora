import logging


class ObserverManager():
    """Class provides an object for subject to manage their observers."""

    def __init__(self):
        self.list_of_observers = []
        self.list_of_observations = []

    def add_observer(self, observer):
        if observer not in self.list_of_observers:
            #try:
            observer.update_observer()
            #except AttributeError: # if it doesn't have the attribute
            #except TypeError: #if it has an attribute that is not a callable method
            self.list_of_observers.append(observer)

    def del_observer(self, observer):
        if observer in self.list_of_observers:
            self.list_of_observers.remove(observer)

    def update_all(self):
        for observer in self.list_of_observers:
            observer.update_observer()
