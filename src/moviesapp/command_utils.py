# coding: utf-8
from __future__ import unicode_literals

import sys

from django.core.management.base import BaseCommand as BaseCommandOriginal
from django.core.management.color import color_style
from tqdm import tqdm as tqdm_original

class BaseCommand(BaseCommandOriginal):
    def print_(self, text, fatal, error=False): # TODO make it private
        text = unicode(text)
        if error:
            output = self.stderr
        else:
            output = self.stdout
        output.write(text)
        if fatal:
            sys.exit()

    def error(self, text, fatal=False):
        self.print_(text, fatal, error=True)

    def info(self, text, fatal=False):
        self.print_(text, fatal)

    # TODO add tqdm here


class tqdm(tqdm_original):
    def __init__(self, *args, **kwargs):
        self.isatty = sys.stdout.isatty()
        if 'disable' not in kwargs:
            kwargs['disable'] = not self.isatty
        # Don't show traces of progress bar by default. We will still see them if error occurs.
        if 'leave' not in kwargs:
            kwargs['leave'] = False
        super(tqdm, self).__init__(*args, **kwargs)

    def print_(self, text, fatal, error=False): # TODO make it private
        if error:
            text = unicode(text)
            text = color_style().ERROR(text)
        if self.isatty:
            self.write(text)
            if fatal:
                sys.exit()
        else:
            command = BaseCommand()
            if error:
                command.error(text, fatal)
            else:
                command.info(text, fatal)

    def error(self, text, fatal=False):
        self.print_(text, fatal, error=True)

    def info(self, text, fatal=False):
        self.print_(text, fatal)
