#!/usr/bin/env python
from formsfive.attributes import *
from itertools import chain


def single_attributes(self):
    '''
    Build a string that contains single
    HTML5 input attributes.
    '''
    elements = list()
    if self.is_required and not self.disabled:
        elements.append(u'required')
    if self.autofocus:
        elements.append(u'autofocus')
    if self.disabled:
        elements.append(u'disabled')
    return ' '.join(chain(elements))


def create_attributes(self, *args):
    '''
    Simple method to construct the
    html5 attributes needed
    '''
    listed = list()
    for arg in args:
        for value in arg:
            listed.append(value)
    check = tuple(listed)
    return dict([(key, values) for key, values in self.__dict__.items() if key in check and values not in EMPTY_VALUES])


def update_widget(self):
    '''
    Use this is order to render HTML single attribute correctly.
    This is mostly used for multiple widgets
    '''
    #lets assume some disfaults
    self.autofocus = self.attrs.get('autofocus', False)
    self.disabled = self.attrs.get('disabled', False)

    defaults = dict([(key, val) for key, val in self.attrs.items() if key in WIDGETS])
    self.__dict__.update(defaults)
    self.attrs = dict(item for item in self.attrs.iteritems() if item not in defaults.items())
    return self


def check_default(self, check):
    if str(self.autocapitalize) != check['autocapitalize']:
            self.widget.autocapitalize = self.autocapitalize

    if str(self.autocorrect) != check['autocorrect']:
        self.widget.autocorrect = self.autocorrect

    if str(self.autofocus) != check['autofocus']:
        self.widget.autofocus = self.autofocus

    if str(self.disabled) != check['disabled']:
        self.widget.disabled = self.disabled

    if str(self.pattern) != check['pattern']:
        self.widget.pattern = self.pattern

    if str(self.placeholder) != check['placeholder']:
        self.widget.placeholder = self.placeholder

    if str(self.readonly) != check['readonly']:
        self.widget.readonly = self.readonly

    if str(self.results) != check['results']:
        self.widget.results = self.results

    if str(self.spellcheck) != check['spellcheck']:
        self.widget.spellcheck = self.spellcheck

    if str(self.min) != check['min']:
        self.widget.min = self.min

    if str(self.max) != check['max']:
        self.widget.max = self.max

    if str(self.step) != check['step']:
        self.widget.step = self.step

    return self
