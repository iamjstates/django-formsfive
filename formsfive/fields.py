#!/usr/bin/env python
from django.utils.encoding import StrAndUnicode, smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django import forms as original
from django.core import validators
from formsfive.utils import check_default
import re, inspect

from django.utils.html import escape

from formsfive.widgets import (
	HTML5Input, TextInput, HiddenInput, CheckboxInput, Select,
    ClearableFileInput, SelectMultiple,
    DateInput, DateTimeInput, TimeInput, URLInput,
    NumberInput, EmailInput, NullBooleanSelect,
    SlugInput, IPAddressInput, SplitDateTimeWidget,
    SplitHiddenDateTimeWidget, PasswordInput
)

EMPTY_VALUES = (None, '', 'NoneType')

__all__ = (
    'Field', 'HTML5Field', 'CharField', 'IntegerField',
    'DateField', 'TimeField', 'DateTimeField', 'EmailField', 'FileField',
    'ImageField', 'URLField', 'BooleanField', 'NullBooleanField', 'ChoiceField',
    'MultipleChoiceField', 'FloatField', 'DecimalField', 'SlugField', 'RegexField',
    'IPAddressField', 'TypedChoiceField', 'FilePathField', 'TypedMultipleChoiceField',
    'ComboField', 'MultiValueField', 'SplitDateTimeField', 'PasswordField'
)


class Field(original.Field):
    pass


class HTML5Field(object):
    widget = HTML5Input
    hidden_widget = HiddenInput

    def __init__(
            self, placeholder=None, autofocus=False, autocapitalize='off',
            autocorrect='off', pattern=None, readonly=False, results=None,
            spellcheck='off', disabled=False, min=False, max=False, step=1, *args, **kwargs):
        super(HTML5Field, self).__init__(*args, **kwargs)
        self.placeholder, self.autofocus, self.autocapitalize = placeholder, autofocus, autocapitalize
        self.autocorrect, self.pattern, self.readonly, self.results = autocorrect, escape(pattern), readonly, results
        self.spellcheck, self.disabled, self.min, self.max, self.step = spellcheck, disabled, min, max, step

        # inspect the __init__ method and get default values
        args, varargs, kwords, defaults = inspect.getargspec(HTML5Field.__init__)
        g = inspect.formatargspec(args[1:], None, None, defaults)[1:-1]

        check = dict()
        # create a dictionary to check default values
        for item in g.split(", "):
            key, val = item.split("=")
            check[key] = val

        # compare default values and change if necessary
        # if you find a better way feel free !! TODO !!
        check_default(self, check)


class PasswordField(HTML5Field, original.CharField):
    widget = PasswordInput


class CharField(HTML5Field, original.CharField):
    widget = TextInput


class BooleanField(HTML5Field, original.BooleanField):
    widget = CheckboxInput


class NullBooleanField(HTML5Field, original.NullBooleanField):
    widget = NullBooleanSelect


class ChoiceField(HTML5Field, original.ChoiceField):
    widget = Select


class TypedChoiceField(ChoiceField, original.TypedChoiceField):
    widget = Select


class FilePathField(ChoiceField, original.FilePathField):
    widget = Select


class FileField(HTML5Field, original.FileField):
    widget = ClearableFileInput


class ImageField(HTML5Field, original.ImageField):
    widget = ClearableFileInput


class MultipleChoiceField(HTML5Field, original.MultipleChoiceField):
    widget = SelectMultiple


try:
    Parent = original.TypedMultipleChoiceField
except AttributeError:  # Django < 1.3
    class Parent(original.MultipleChoiceField):
        """No-op class for older Django versions"""
        def __init__(self, *args, **kwargs):
            kwargs.pop('coerce', None)
            kwargs.pop('empty_value', None)
            super(Parent, self).__init__(*args, **kwargs)


class TypedMultipleChoiceField(MultipleChoiceField, Parent):
    pass


class DateField(HTML5Field, original.DateField):
    widget = DateInput


class DateTimeField(HTML5Field, original.DateTimeField):
    widget = DateTimeInput


class TimeField(HTML5Field, original.TimeField):
    widget = TimeInput


class DecimalField(HTML5Field, original.DecimalField):
    widget = NumberInput


class FloatField(HTML5Field, original.FloatField):
    widget = NumberInput


class IntegerField(HTML5Field, original.IntegerField):
    widget = NumberInput

    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)


class EmailField(HTML5Field, original.EmailField):
    widget = EmailInput


class URLField(HTML5Field, original.URLField):
    widget = URLInput


class SlugField(HTML5Field, original.SlugField):
    widget = SlugInput


class RegexField(CharField):
    widget = TextInput

    def __init__(self, regex, error_message=None, *args, **kwargs):
        """
        This will be going away soon
        """
        if error_message:
            error_messages = kwargs.get('error_messages') or {}
            error_messages['invalid'] = error_message
            kwargs['error_messages'] = error_messages
        pattern = regex
        super(RegexField, self).__init__(*args, **kwargs)
        if isinstance(regex, basestring):
            regex = re.compile(regex)
        self.regex = regex
        self.widget.pattern = pattern
        self.validators.append(validators.RegexValidator(regex=regex))


class IPAddressField(HTML5Field, original.IPAddressField):
    widget = IPAddressInput


class ComboField(HTML5Field, original.ComboField):
    pass


class MultiValueField(HTML5Field, original.MultiValueField):
    pass


class SplitDateTimeField(original.SplitDateTimeField):
    widget = SplitDateTimeWidget
    hidden_widget = SplitHiddenDateTimeWidget

    def __init__(self, *args, **kwargs):
        super(SplitDateTimeField, self).__init__(*args, **kwargs)
        for widget in self.widget.widgets:
            widget.is_required = self.required
