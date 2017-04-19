# coding: utf-8
from __future__ import unicode_literals

import sys

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from tqdm import tqdm as tqdm_original


class tqdm(tqdm_original):
    def __init__(self, *args, **kwargs):
        self.isatty = sys.stdout.isatty()
        # We don't want a progress bar if we just have one movie
        if kwargs['total'] == 1:
            kwargs['disable'] = True
        if 'disable' not in kwargs:
            kwargs['disable'] = not self.isatty
        if 'leave' not in kwargs:
            kwargs['leave'] = False
        super(tqdm, self).__init__(*args, **kwargs)

    def print_(self, text, error=False):
        text = unicode(text)
        if error:
            text = color_style().ERROR(text)
        if self.isatty:
            output = self
        else:
            command = BaseCommand()
            if error:
                output = command.stderr
            else:
                output = command.stdout
        output.write(text)

    def error(self, text):
        self.print_(text, True)

    def info(self, text):
        self.print_(text)
