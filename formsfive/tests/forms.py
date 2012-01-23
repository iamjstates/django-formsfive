#!/usr/bin/env python
from django.utils.translation import ugettext_lazy as _
from formsfive.tests.models import Todo
import formsfive as forms


class TodoForm(forms.HTML5ModelForm):
    body = forms.CharField(label=_(u'Post or Story Body'), placeholder=_(u'listed'), required=True)

    class Meta:
        model = Todo
        exclude = ('slug', 'date')

    def __init__(self, *args, **kwargs):
        super(TodoForm, self).__init__(*args, **kwargs)
        self.fields['task'].widget.placeholder = _(u'A Task to do')
        self.fields['units'].widget.min = 0
        self.fields['units'].widget.max = 100
        self.fields['units'].widget.step = 2
