#!/usr/bin/env python
from formsfive.widgets import Select, SelectMultiple
from django.forms import models

__all__ = ('ModelChoiceField', 'ModelMultipleChoiceField')


class ModelChoiceField(models.ModelChoiceField):
    widget = Select


class ModelMultipleChoiceField(models.ModelMultipleChoiceField):
    widget = SelectMultiple