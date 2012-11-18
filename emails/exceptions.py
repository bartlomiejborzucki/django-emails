#-*- coding: utf-8 -*-
__author__ = 'freeman'





class Diffrent_emails(Exception):
    """
        Wyjątek jest wyrzucany, zmienna email i user.email się różnią
    """
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class Email_is_empty(Exception):
    """
        Wyjątek jest wyrzucany, zmienna email i user.email się różnią
    """
    def __init__(self):
        self.parameter = "Pole email jest puste"
    def __str__(self):
        return repr(self.parameter)
