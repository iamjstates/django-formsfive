#!/usr/bin/env python
from formsfive.widgets import Select, SelectMultiple, Textarea
from django.forms.forms import get_declared_fields
from django.utils.datastructures import SortedDict
from django.forms.widgets import media_property
from django.core.exceptions import FieldError
from django.forms import models as original
from formsfive import fields as five
from django.db import models


__all__ = ('ModelChoiceField', 'ModelMultipleChoiceField', 'HTML5ModelForm')


class ModelChoiceField(original.ModelChoiceField):
    widget = Select


class ModelMultipleChoiceField(original.ModelMultipleChoiceField):
    widget = SelectMultiple


HTML5FIELD_FOR_DBFIELD = {
    models.BigIntegerField:             {'form_class': five.IntegerField},
    models.BooleanField:                {'form_class': five.BooleanField},
    models.CharField:                   {'form_class': five.CharField},
    models.DateField:                   {'form_class': five.DateField},
    models.DateTimeField:               {'form_class': five.DateTimeField},
    models.DecimalField:                {'form_class': five.DecimalField},
    models.EmailField:                  {'form_class': five.EmailField},
    models.FileField:                   {'form_class': five.FileField},
    models.FilePathField:               {'form_class': five.FilePathField},
    models.FloatField:                  {'form_class': five.FloatField},
    models.ForeignKey:                  {'form_class': ModelChoiceField},
    models.ImageField:                  {'form_class': five.ImageField},
    models.IntegerField:                {'form_class': five.IntegerField},
    models.IPAddressField:              {'form_class': five.IPAddressField},
    models.ManyToManyField:             {'form_class': ModelMultipleChoiceField},
    models.NullBooleanField:            {'form_class': five.CharField},
    models.PositiveIntegerField:        {'form_class': five.IntegerField},
    models.PositiveSmallIntegerField:   {'form_class': five.IntegerField},
    models.SlugField:                   {'form_class': five.SlugField},
    models.SmallIntegerField:           {'form_class': five.IntegerField},
    models.PositiveIntegerField:        {'form_class': five.IntegerField},
    models.PositiveSmallIntegerField:   {'form_class': five.IntegerField},
    models.TimeField:                   {'form_class': five.TimeField},
    models.TextField:                   {'form_class': five.SplitDateTimeField, 'widget': Textarea},
    models.URLField:                    {'form_class': five.URLField},
}


class _BaseForm(object):
    def clean(self):
        for field in self.cleaned_data:
            if isinstance(self.cleaned_data[field], basestring):
                self.cleaned_data[field] = self.cleaned_data[field].strip()
        return self.cleaned_data


def fields_for_model(model, fields=None, exclude=None, widgets=None, formfield_callback=None):
    """
    Returns a ``SortedDict`` containing form fields for the given model.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned fields.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned fields, even if they are listed
    in the ``fields`` argument.

    add HTML5FIELD to call the HTML5 form
    """
    field_list = []
    ignored = []
    opts = model._meta
    for f in sorted(opts.fields + opts.many_to_many):
        if not f.editable:
            continue
        if fields is not None and not f.name in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if widgets and f.name in widgets:
            kwargs = {'widget': widgets[f.name]}
        else:
            kwargs = {}

        if formfield_callback is None:
            try:
                # Change the dbfield to the html5 forms
                kwargs = dict(HTML5FIELD_FOR_DBFIELD[f.__class__], **kwargs)
            except:
                kwargs = {}
            formfield = f.formfield(**kwargs)
        elif not callable(formfield_callback):
            raise TypeError('formfield_callback must be a function or callable')
        else:
            formfield = formfield_callback(f, **kwargs)

        if formfield:
            field_list.append((f.name, formfield))
        else:
            ignored.append(f.name)
    field_dict = SortedDict(field_list)
    if fields:
        field_dict = SortedDict(
            [(f, field_dict.get(f)) for f in fields
                if ((not exclude) or (exclude and f not in exclude)) and (f not in ignored)]
        )
    return field_dict


class HTML5ModelFormMetaclass(type):
    def __new__(cls, name, bases, attrs):
        formfield_callback = attrs.pop('formfield_callback', None)
        try:
            parents = [b for b in bases if issubclass(b, HTML5ModelForm)]
        except NameError:
            # We are defining ModelForm itself.
            parents = None
        declared_fields = get_declared_fields(bases, attrs, False)
        new_class = super(HTML5ModelFormMetaclass, cls).__new__(cls, name, bases,
                attrs)
        if not parents:
            return new_class

        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = new_class._meta = original.ModelFormOptions(getattr(new_class, 'Meta', None))
        if opts.model:
            # If a model is defined, extract form fields from it.
            fields = fields_for_model(opts.model, opts.fields,
                                      opts.exclude, opts.widgets, formfield_callback)
            # make sure opts.fields doesn't specify an invalid field
            none_model_fields = [k for k, v in fields.iteritems() if not v]
            missing_fields = set(none_model_fields) - \
                             set(declared_fields.keys())
            if missing_fields:
                message = 'Unknown field(s) (%s) specified for %s'
                message = message % (', '.join(missing_fields),
                                     opts.model.__name__)
                raise FieldError(message)

            fields.update(declared_fields)
        else:
            fields = declared_fields
        new_class.declared_fields = declared_fields
        new_class.base_fields = fields
        return new_class


class HTML5ModelForm(_BaseForm, original.BaseModelForm):
    __metaclass__ = HTML5ModelFormMetaclass
