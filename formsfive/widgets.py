#!/usr/bin/env python
from formsfive.utils import create_attributes, single_attributes
from django.utils.html import escape, conditional_escape
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt
from formsfive.utils import update_widget
from formsfive.attributes import *
from django.forms import widgets
from itertools import chain
import re

__all__ = (
    'CheckboxInput', 'CheckboxSelectMultiple', 'ClearableFileInput', 'ColorInput',
    'DataListInput', 'DateInput', 'DateTimeInput', 'DateTimeLocalInput',
    'EmailInput', 'FileInput', 'HiddenInput', 'IPAddressInput',
    'MonthInput', 'MultiWidget', 'MultipleHiddenInput', 'NullBooleanSelect',
    'NumberInput', 'PasswordInput', 'RadioSelect', 'RangeInput',
    'SearchInput', 'Select', 'SelectMultiple', 'SplitDateTimeWidget',
    'SplitHiddenDateTimeWidget', 'Textarea', 'TelephoneInput', 'TextInput',
    'TimeInput', 'WeekInput', 'Widget', 'URLInput',
)


class Widget(widgets.Widget):
    pass


class BaseInput(widgets.Widget):
    '''
    Customer base class for all <input> widgets (except type='checkbox' and
    type='radio', which are special).
    This produces html5 input and should reduce code.
    If you want to override the default placeholder value just place it in
    widget=HTMLInput(placeholder='some value')
    '''
    input_type = None

    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, placeholder=self.placeholder, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(self._format_value(value))
        if self.is_required:
            return mark_safe(u'<input%s required>' % flatatt(final_attrs))
        else:
           return mark_safe(u'<input%s>' % flatatt(final_attrs))


class HTML5Input(BaseInput):
    '''
    This adds html 5 formatted specs in forms
    This is be bit more verbose than default widget as
    I override the __init__ method and prefer to set what
    attributes are needed there.

    You are still able to build_attrs the normal way in when
    extending other widgets.
    '''
    # setup common input attributes
    input_type = 'text'

    def __init__(self, attrs=None, *args, **kwargs):
        super(HTML5Input, self).__init__(attrs, *args, **kwargs)
        '''
        Look for HTML5 attributes to override and provide default
        values for them.

        I keep these values to allow the traditional widget method.
        (i.e. form(widgets=TextInput(attrs={'placeholder': 'Sample'})))

        !!! This is not recommended - violates DRY !!!
        '''
        # Use this is order to render HTML single attribute correctly.
        # You will use mostly for multiple widgets
        update_widget(self)
        self.autocorrect =  self.attrs.get('autocorrect', 'off')
        self.autocapitalize = self.attrs.get('autocapitalize', 'off')
        self.results = self.attrs.get('results', None)
        self.readonly = self.attrs.get('readonly', None)

    def render(self, name, value, attrs=None, new_attrs=None, elements=None):
        # build a list of possible elements
        if not elements:
            elements = single_attributes(self)

        if not new_attrs:
            # below removes empty attributes and also removes dictionary of attributes that are not longer necessary
            new_attrs = create_attributes(self, UNIVERSAL, TEXT_SEARCH)

        if value is None: value = ''
        # set default
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name, **new_attrs)

        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            # This adds non-dictionary items to the input field such as required
            final_attrs['value'] = force_unicode(value)

        return mark_safe(u'<input%s %s>' % (flatatt(final_attrs), elements))

    def format_value(self, value):
        if value != '':
            value = force_unicode(value)
        return value


class TextInput(widgets.TextInput, HTML5Input):
    input_type = 'text'

    def __init__(self, attrs=None):
        default_attrs = {'pattern': '[\w]+'}
        if attrs:
            default_attrs.update(final_attrs)
        super(TextInput, self).__init__(default_attrs)

    def render(self, name, value, attrs):
        new_attrs =  create_attributes(self, UNIVERSAL, TEXT_SEARCH)
        return HTML5Input.render(self, name, value, attrs, new_attrs)


class PasswordInput(widgets.PasswordInput, HTML5Input):
    input_type = 'password'

    def render(self, name, value, attrs=None):
        new_attrs =  create_attributes(self, UNIVERSAL, PASSWORD)
        if not self.render_value: value=None
        return HTML5Input.render(self, name, value, attrs, new_attrs)

    def format_value(self, value):
        return value


class SearchInput(HTML5Input):
    input_type = 'search'

    def __init__(self, attrs=None):
        default_attrs = {'placeholder': _(u'Search')}
        if attrs:
            default_attrs.update(attrs)
        super(SearchInput, self).__init__(default_attrs)


class HiddenInput(widgets.HiddenInput, HTML5Input):
    input_type = 'hidden'
    is_hidden = True

    def render(self, name, value, attrs):
        new_attrs =  create_attributes(self, UNIVERSAL, TEXT_SEARCH)
        return HTML5Input.render(self, name, value, attrs, new_attrs)


class MultipleHiddenInput(widgets.HiddenInput, HTML5Input):
    '''
    !!WORK-ON!!

    '''
    input_type = 'hidden'
    is_hidden = True

    def __init__(self, attrs=None, choices=()):
        super(MultipleHiddenInput, self).__init__(attrs)
        self.choices = choices

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []

        new_attrs =  create_attributes(self, UNIVERSAL, TEXT_SEARCH)

        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)

        id_ = final_attrs.get('id', None)
        inputs = []
        for i, v in enumerate(value):
            input_attrs = dict(value=force_unicode(v), **final_attrs)
            if id_:
                input_attrs['id'] = '%s_%s' % (id_, i)
            del input_attrs['type']
            del input_attrs['value']
            input_ = HiddenInput()
            input_.is_required = self.is_required
            inputs.append(input_.render(name, force_unicode(v), input_attrs))
        return "\n".join(inputs)


class SlugInput(HTML5Input):
    def __init__(self, attrs=None):
        default_attrs = {'pattern': '[\w-]+'}
        if attrs:
            default_attrs.update(attrs)
        super(SlugInput, self).__init__(default_attrs)

    def render(self, name, value, attrs):
        new_attrs =  create_attributes(self, UNIVERSAL, TEXT_SEARCH)
        return HTML5Input.render(self, name, value, attrs, new_attrs)


class IPAddressInput(widgets.TextInput, HTML5Input):
    def __init__(self, attrs=None):
        default_attrs = {'pattern': '(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'}
        if attrs:
            default_attrs.update(attrs)
        super(IPAddressInput, self).__init__(default_attrs)

    def render(self, name, value, attrs):
        new_attrs =  create_attributes(self, UNIVERSAL, TEXT_SEARCH)
        return HTML5Input.render(self, name, value, attrs, new_attrs)


class CheckboxInput(widgets.CheckboxInput, HTML5Input):
    input_type = 'checkbox'

    def render(self, name, value, attrs=None, elements=None, choices=()):
        new_attrs =  create_attributes(self, UNIVERSAL, CHOICE)
        elements = single_attributes(self)
        final_attrs = self.build_attrs(attrs, name=name, type="checkbox", **new_attrs)
        try:
            result = self.check_test(value)
        except: # Silently catch exceptions
            result = False
        if result:
            final_attrs['checked'] = 'checked'
        if value not in ('', True, False, None):
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'<input%s %s>' % (flatatt(final_attrs), elements))


class Select(widgets.Select, HTML5Input):
    def __init__(self, attrs=None, choices=()):
        super(Select, self).__init__(attrs)
        self.choices = list(choices)

    def render(self, name, value, attrs=None, choices=()):
        new_attrs =  create_attributes(self, UNIVERSAL, SELECT)
        # build a list of possible elements
        elements = single_attributes(self)
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name, **new_attrs)
        output = [u'<select%s %s>' % (flatatt(final_attrs), elements)]
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append(u'</select>')
        return mark_safe(u'\n'.join(output))

    def render_option(self, selected_choices, option_value, option_label):
        if not isinstance(option_value, (unicode)):
            option_value = force_unicode(option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        return u'<option value="%s"%s>%s</option>' % (
            escape(option_value), selected_html,
            conditional_escape(force_unicode(option_label)))

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(output)


class NullBooleanSelect(widgets.NullBooleanSelect, Select):

    def render(self, name, value, attrs=None, choices=()):
        choices = ((u'1', _(u'Unknown')),
                   (u'2', _(u'Yes')),
                   (u'3', _(u'No')))
        try:
            value = {True: u'2', False: u'3', u'2': u'2', u'3': u'3'}[value]
        except KeyError:
            value = u'1'
        return Select.render(self, name, value, attrs, choices=choices)


class Textarea(HTML5Input, widgets.Textarea):

    def render(self, name, value, attrs=None):
        new_attrs =  create_attributes(self, UNIVERSAL, TEXT_SEARCH)
        attrs.update(**new_attrs)
        elements = single_attributes(self)
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<textarea%s %s>%s</textarea>' % (flatatt(final_attrs),
                elements, conditional_escape(force_unicode(value))))


class FileInput(HTML5Input, widgets.FileInput):
    input_type = 'file'
    needs_multipart_form = True


class SelectMultiple(Select):

    def render(self, name, value, attrs=None, choices=()):
        new_attrs =  create_attributes(self, UNIVERSAL, SELECT)
        # build a list of possible elements
        elements = single_attributes(self)
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name, **new_attrs)
        output = [u'<select multiple="multiple"%s %s>' % (flatatt(final_attrs), elements)]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append(u'</select>')
        return mark_safe(u'\n'.join(output))


class RadioInput(widgets.RadioInput, HTML5Input):

    def __init__(self, name, value, attrs, choice, index, elements=None):
        self.name, self.value = name, value
        self.attrs = attrs
        self.choice_value = force_unicode(choice[0])
        self.choice_label = force_unicode(choice[1])
        self.index = index
        self.elements = elements

    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'<label%s>%s %s</label>' % (label_for, self.tag(), choice_label))

    def tag(self):
        new_attrs =  create_attributes(self, UNIVERSAL)
        #attrs.update(**new_attrs)
        self.attrs.update(**new_attrs)
        if self.elements:
            elements = self.elements
        else:
            elements = single_attributes(self)
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return mark_safe(u'<input%s %s>' % (flatatt(final_attrs), elements))


class CheckboxSelectMultiple(SelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))


class RadioSelect(widgets.RadioSelect, HTML5Input):

    def render(self, name, value, attrs=None, choices=()):
        new_attrs =  create_attributes(self, UNIVERSAL)
        # build a list of possible elements
        elements = single_attributes(self)
        attrs.update(**new_attrs)

        output = list()
        for i, choice in enumerate(self.choices):
            output.append(RadioInput(name, value, attrs.copy(), choice, i, elements))

        return mark_safe(u'<ul>\n%s\n</ul>' % u'\n'.join([u'<li>%s</li>'
                % force_unicode(w) for w in output]))


class MultiWidget(widgets.MultiWidget, HTML5Input):

    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []

        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
        return mark_safe(self.format_output(output))


class ClearableFileInput(HTML5Input, widgets.ClearableFileInput):
    input_type = 'file'
    needs_multipart_form = True

    def render(self, name, value, attrs=None):
        new_attrs =  create_attributes(self, UNIVERSAL)
        # build a list of possible elements
        elements = single_attributes(self)

        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs, new_attrs, elements)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = (u'<a href="%s">%s</a>'
                                        % (escape(value.url),
                                           escape(force_unicode(value))))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)

    def format_value(self, value):
        return value


class DateInput(widgets.DateInput, HTML5Input):
    input_type = 'date'

    def render(self, name, value, attrs):
        new_attrs =  create_attributes(self, UNIVERSAL, TIME_NUMERIC)
        return HTML5Input.render(self, name, value, attrs, new_attrs)


class TimeInput(widgets.TimeInput, HTML5Input):
    input_type = 'time'

    def render(self, name, value, attrs):
        new_attrs =  create_attributes(self, UNIVERSAL, TIME_NUMERIC)
        return HTML5Input.render(self, name, value, attrs, new_attrs)


class SplitDateTimeWidget(MultiWidget):
    def __init__(self, attrs=None, date_format=None, time_format=None):
        widgets = (DateInput(attrs=attrs, format=date_format),
                   TimeInput(attrs=attrs, format=time_format))
        super(SplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]


class SplitHiddenDateTimeWidget(SplitDateTimeWidget):
    is_hidden = True

    def __init__(self, attrs=None, date_format=None, time_format=None):
        super(SplitHiddenDateTimeWidget, self).__init__(attrs, date_format,
                                                        time_format)
        for widget in self.widgets:
            widget.input_type = 'hidden'
            widget.is_hidden = True


class EmailInput(HTML5Input):
    input_type = 'email'

    def __init__(self, attrs=None):
        default_attrs = {
            'pattern': '/^((?!@)\S)+[@]((?!@)\S)+/',
            'placeholder': _(u'(i.e. address@domain.com)')}
        if attrs:
            default_attrs.update(attrs)
        super(EmailInput, self).__init__(default_attrs)


class URLInput(HTML5Input):
    input_type = 'url'

    def __init__(self, attrs=None):
        default_attrs = {
            'placeholder': _(u'(i.e. http://domain.com)')}
        if attrs:
            default_attrs.update(attrs)
        super(URLInput, self).__init__(default_attrs)


class TelephoneInput(HTML5Input):
    input_type = 'tel'


class NumberInput(HTML5Input):
    input_type = 'number'
    min = None
    max = None
    step = None

    def __init__(self, attrs=None):
        default_attrs = {'min': self.min, 'max': self.max, 'step': self.step}
        if attrs:
            default_attrs.update(attrs)
        super(NumberInput, self).__init__(default_attrs)


class RangeInput(NumberInput):
    input_type = 'range'


class MonthInput(DateInput):
    input_type = 'month'


class WeekInput(DateInput):
    input_type = 'week'


class DateTimeInput(DateInput):
    input_type = 'datetime'


class DateTimeLocalInput(DateInput):
    input_type = 'datetime-local'


class ColorInput(HTML5Input):
    input_type = 'color'


class DataListInput(HTML5Input, widgets.Select):
    input_type = 'text'
    list = None

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        new_attrs =  create_attributes(self, UNIVERSAL, TEXT_SEARCH)
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name, list=name, **new_attrs)
        output = list()
        output.append(u'<input%s />' % flatatt(final_attrs))
        output.append(u'<datalist id="%(name)s">' % final_attrs)
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append(u'</datalist>')
        return mark_safe(u'\n'.join(output))
