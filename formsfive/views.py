from django.shortcuts import render_to_response
from formsfive.testforms import TextForm


def example(request, default_template='form.tpl', form_class=TextForm):
    options = dict()
    options['form'] = form_class(request.POST or None)
    return render_to_response(default_template, options)
