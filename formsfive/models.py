#!/usr/bin/env python
from django.core.exceptions import FieldError, NON_FIELD_ERRORS
from formsfive.widgets import Select, SelectMultiple, Textarea
from django.forms.forms import Form, get_declared_fields
from django.utils.datastructures import SortedDict
from django.forms.widgets import media_property
from django.utils.safestring import mark_safe
from django.db import models as original
from formsfive import fields as five
from django.forms import models

__all__ = ('ModelChoiceField', 'ModelMultipleChoiceField')


class ModelChoiceField(models.ModelChoiceField):
    widget = Select


class ModelMultipleChoiceField(models.ModelMultipleChoiceField):
    widget = SelectMultiple


HTML5FIELD_FOR_DBFIELD = {
    original.BigIntegerField:           {'form_class': five.BigIntegerField},
    original.BooleanField:              {'form_class': five.BooleanField},
    original.CharField:                 {'form_class': five.CharField},
    original.DateField:                 {'form_class': five.DateField},
    original.DateTimeField:             {'form_class': five.DateTimeField},
    original.DecimalField:              {'form_class': five.DecimalField},
    original.EmailField:                {'form_class': five.EmailField},
    original.FileField:                 {'form_class': five.FileField},
    original.FilePathField:             {'form_class': five.FilePathField},
    original.FloatField:                {'form_class': five.FloatField},
    original.ForeignKey:                {'form_class': ModelChoiceField},
    original.ImageField:                {'form_class': five.ImageField},
    original.IntegerField:              {'form_class': five.IntegerField},
    original.IPAddressField:            {'form_class': five.IPAddressField},
    original.ManyToManyField:           {'form_class': ModelMultipleChoiceField},
    original.NullBooleanField:          {'form_class': five.CharField},
    original.PositiveIntegerField:      {'form_class': five.IntegerField},
    original.PositiveSmallIntegerField: {'form_class': five.IntegerField},
    original.SlugField:                 {'form_class': five.SlugField},
    original.SmallIntegerField:         {'form_class': five.IntegerField},
    original.TimeField:                 {'form_class': five.TimeField},
    original.TextField:                 {'form_class': five.SplitDateTimeField, 'widget': Textarea},
    original.URLField:                  {'form_class': five.URLField},
}


class _BaseForm(object):
    def clean(self):
        for field in self.cleaned_data:
            if isinstance(self.cleaned_data[field], basestring):
                self.cleaned_data[field] = self.cleaned_data[field].strip()
        return self.cleaned_data


class HTML5Form(_BaseForm, Form):

    def print_errors(self):
        errors = []
        for (field, error) in self.errors.items():
            if field != NON_FIELD_ERRORS and self.fields[field].label:
                errors.append(u'<li><span>%s</span>: ' % self.fields[field].label)
            else:
                errors.append(u'<li>')
            errors.append(u'%s</li>' % u"".join([unicode(e) for e in error]))

        if len(errors):
            return mark_safe('<ul class="errors">%s</ul>' % "\n".join(errors))
        else:
            return u""

    def as_p(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(u'<p>%(label)s %(field)s<br /> %(help_text)s</p>', u'%s', '</p>', u' %s', True)

## END ##


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
