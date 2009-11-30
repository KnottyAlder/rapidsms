#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import rapidsms
from rapidsms.djangoproject import settings
from .utils import find_handlers
from . import BaseHandler


class App(rapidsms.App):
    def start(self):
        """
        Spiders all RapidSMS apps, and registers all available handlers.
        """

        self.handlers = []

        for module_name in settings.RAPIDSMS_APPS.keys():
            handlers = find_handlers(module_name)
            self.handlers.extend(handlers)

        class_names = [cls.__name__ for cls in self.handlers]
        self.info("Registered handlers: %s" % (", ".join(class_names)))


    def handle(self, msg):
        """
        Forwards the *msg* to every handler, and short-circuits the
        phase if any of them accept it. The first to accept it will
        block the others, and there's deliberately no way to predict
        the order that they're called in. (This is intended to force
        handlers to be as reluctant as possible.)
        """

        for handler in self.handlers:
            if handler.dispatch(self.router, msg):
                self.info("Incoming message handled by %s" % handler.__name__)
                return True
