#!/usr/bin/env python
from django.utils.encoding import StrAndUnicode, smart_unicode, force_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape
from django.core.exceptions import ValidationError
from django.utils.simplejson import JSONEncoder
from django.utils.safestring import mark_safe
from django.conf import settings
from formsfive.widgets import HTML5Input
from formsfive import widgets


__all__ = (
    'ValidateLoginPassWidget', 'ValidateEmailWidget', 'PreviewWidget', 'AttachWidget',
    'MultipleFocusWidget', 'FocusSelect', 'DatePickerWidget', 'AutoCompleteModelWidget',
    'AutoCompleteTagWidget', 'USPhoneNumberMultiWidget', 'SSNInputWidget', 'GenericWidget',
    'DisplayOnlyWidget'
)


class ValidateLoginPassWidget(widgets.MultiWidget):
    """
    Basic MultiWidget to validate passwords versus
    each other. This returns both values.
    """
    def __init__(self, attrs=None):
        formsfive_widgets = (
            widgets.PasswordInput(render_value=False, attrs={'placeholder': 'Insert your password', 'is_required': True}),
            widgets.PasswordInput(render_value=False, attrs={'placeholder': 'Confirm password', 'is_required': False}),
            )
        super(ValidateLoginPassWidget, self).__init__(formsfive_widgets, attrs)

    def format_output(self, widgets):
        return u'</div>\n<div class="form-default"><label for="password1">Password (Validation): </label>'.join(widgets)

    def decompress(self, value):
        if isinstance(value, dict):
            if value:
                return [value.password, value.password1]
        return [None, None]


class ValidateEmailWidget(widgets.MultiWidget):
    """
    Basic MultiWidget to validate email addresses versus
    each other. This returns both values.
    """
    def __init__(self, attrs=None):
        formsfive_widgets = (
            widgets.TextInput(attrs={'placeholder': 'Email Address', 'is_required': True}),
            widgets.TextInput( attrs={'placeholder': 'Validate Address', 'is_required': False}),
            )
        super(ValidateEmailWidget, self).__init__(formsfive_widgets, attrs)

    def format_output(self, widgets):
        return u'</div>\n<div class="multi"><label for="email1">Email Address (Validation):</label><br />'.join(widgets)

    def decompress(self, value):
        if value:
            return [value.email, value.email1]
        return [None, None]


class PreviewWidget(widgets.FileInput):
    """
    This displays a thumbnail of the image attached to the
    input element - think usabilty.
    """
    def __init__(self, *args, **kwargs):
        super(PreviewWidget, self).__init__(*args, **kwargs)
        self.attrs = kwargs.get('attrs', {})
        self.setting = self.attrs.get('setting', settings.MEDIA_ROOT)

    def render(self, name, value, attrs=None):
        thumb_html = ''
        if value and hasattr(value, "url"):
            # Take value and switch with thumbnail image
            #junk, app_url = str(self.setting).rsplit(str(settings.THEIRRY_MEDIA)) #PRODUCTION
            #app_url = app_url + '/' #PRODUCTION
            #basename, format = str(value).rsplit('.', 1) # PRODUCTION
            basename, format = str(value.name).rsplit('.', 1)
            thumb = basename + '_' + str('thumbnail') + '.' + format
            thumb_html = '<img src="%s/%s" class="thumb" /><br />' % (value.storage.base_url, thumb)
            #thumb_html = '<img src="%s%s%s" class="thumb" /><br />' % (value.storage.base_url, app_url, thumb)
        return mark_safe("%s%s" % (thumb_html, super(PreviewWidget, self).render(name, value, attrs)))


class AttachWidget(widgets.FileInput):
    """
    This basically renders the name of the file attached to this
    input element.
    """
    def __init__(self):
        super(AttachWidget, self).__init__({})

    def render(self, name, value, attrs=None):
        attach_html = ''
        if value not in EMPTY_VALUES:
            attach = u'%s' % value
            attached = os.path.basename(attach)
            attach_html = '<div class=\"attached\" name=\"%s\" >File Attached: %s</div>' % (attached, attached)
        return mark_safe("%s%s" % (attach_html, super(AttachWidget, self).render(name, value, attrs)))


class MultipleFocusWidget(widgets.SelectMultiple):
    '''
    This adds the necessary html and js in order to dynamically
    create this image gallery.  The first appended <ul> preforms
    the correct action functions (view, add, delete).  The last
    appended element allows the addition of selected files to
    be viewed via a modal window.
    '''

    class Media:
        js = (  settings.THEIRRY_MEDIA_URL  + "js/image-form.js",)

    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        super(MultipleFocusWidget, self).__init__(attrs, choices, *args, **kwargs)
        '''
        Look for select attributes to override default
        '''
        self.attrs = kwargs.get('attrs', {})
        self.size = self.attrs.get('size', 5)

    def render(self, name, value, attrs=None, choices=()):
        # add url
        add_url = reverse('generic_images_modal')
        search_url = reverse('search_interchange_modal')
        if attrs is None: attrs = {}
        attrs['class'] = 'multiple add'
        attrs['size'] = self.size
        output = [super(MultipleFocusWidget, self).render(name, value, attrs, choices)]
        output.append(u'''
            <ul id="file-action" class="multiplefilechooser">
                <li><a href="#id_image" id="view-file" name="view" class="form-elements file-view" title="View">View</a></li>
                <li><a href="%s" id="folder-file" name="remove" class="form-elements file-folder" title="From Theirry Library">File</a></li>
                <li><a href="%s" id="add-file" name="add" class="form-elements file-add" title="Add">Add</a></li>
                <li><a href="#id_image" id="remove-file" name="remove" class="form-elements file-remove" title="Remove">Remove</a></li>
            </ul>
            ''' % (search_url, add_url))
        output.append(u'''
            <article id="image" style="z-index: 12; opacity: 1; display: none;" >
                <div id="image-close"><a href="#" class="simplemodal-close">x</a></div>
                <h1 id="modal-title"></h1>

                <div id="modal-area">
                </div>
            </article>
            ''')
        return mark_safe(u''.join(output))

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        if len(selected_choices) == 0:
            image = 'none'
        else:
            # TODO - this gives you the url to see that image
            uri = self.choices.queryset.get(pk=option_value)
            image = uri.image.image.url

        return u'<option value="%s"id="%s"%s>%s</option>' % (
            escape(option_value), image, selected_html,
            conditional_escape(force_unicode(option_label)))


class FocusSelect(widgets.Select): #TODO - change to (SelectMultiple)
    """
    This is a basic select multiple widget, but checks if the data
    changed based of the initial values set forth in the first pass.
    """
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select multiple="multiple" class="focus"%s>' % flatatt(final_attrs)]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe(u'\n'.join(output))

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        for value1, value2 in zip(initial, data):
            if force_unicode(value1) != force_unicode(value2):
                return True
        return False


class DatePickerWidget(widgets.TextInput):
    '''
    Renders all the necessary code for datepicker-addon jquery
    field. This uses the yepnope is an asynchronous conditional resource loader.
    If your using this outside of the my application please:
    CHECK YOUR SETTING LOCATIONS
    '''
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        self.options = dict()
        self.options = {
            'id': str(final_attrs.get('id', None)), 'static': settings.THEIRRY_MEDIA_URL
        }

        output = [super(DatePickerWidget, self).render(name, value, attrs)]
        output.append(
           u'''
            <script>

                yepnope({
                    load:[
                        '%(static)sjs/jquery.js', %(static)sjs/jquery-ui-1.8.15.custom.js, %(static)sjs/jquery-ui-timepicker-addon.js
                    ],
                    complete: function(){
                        jQuery(function(){

                            var %(id)s = $('#%(id)s');

                            %(id)s.datetimepicker({
                                timeFormat: 'hh:mm:ss TT',
                                ampm: true,
                                hourMin: 0,
                                minuteMin: 0,
                                secondMin: 0,
                                stepMinute: 5,
                            });

                            $('#%(id)s_button').click(function(){
                                %(id)s.datetimepicker('setDate', (new Date()) );
                            });

                        });
                    }
                });

            </script>
            ''' % (self.options)
        )
        return mark_safe(u''. join(output))

        css = {
            'all': (
                '%scss/theirry/jquery-ui-1.8.15.custom.css' % settings.THEIRRY_MEDIA_URL,
            )
        }


class AutoCompleteModelWidget(widgets.TextInput):
    '''
    Usage:
    tags = TagField(widget=AutoCompleteTagWidget(attrs={'app': 'your application name', 'model': 'your model', 'source': 'tag_lookup', 'length': 2}), required=False)
    '''
    def __init__(self, options=dict(), *args, **kwargs):
        self.options = options
        super(AutoCompleteModelWidget, self).__init__(*args, **kwargs)
        if self.options.get('length') in EMPTY_VALUES:
            self.length = 2
        else:
            self.length = self.options.get('length', 2) # default to 2 letters

        if isinstance(self.options.get('model'), Model):
            self.model = self.options.get('model')
        else:
            pass

        if self.options.has_key('uri'):
            if isinstance(self.options['uri'], basestring):
                self.is_url = True
                self.uri = self.options.get('uri')
        else:
            self.options['disabled'] = 'true'
            self.uri = '/'

    class Media:
        css = {'all': ('%scss/autocomplete.css' % settings.THEIRRY_MEDIA_URL,)}

    def render(self, name, value, attrs=None):

        if self.options['uri'].find('/') == -1 and self.is_url:
            # Some occasions the url is present, check to see if present if not preform function
            try:
                self.uri = reverse(self.options['uri'])
            except NoReverseMatch:
                # seems to be an error -> disable search
                self.uri = '/'

        self.options = {
            'id': attrs['id'], 'uri': self.uri,
            'length': self.length, 'static': settings.THEIRRY_MEDIA_URL,
        }

        if value in EMPTY_VALUES or len(value) == 0:
            value = ''
        else:
            complete_list = list()

            if isinstance(value, QuerySet):
                for v in value:
                    complete_list.append(v.tag.name)
                value = ', '.join(complete_list)

            if isinstance(value, unicode):
                pass

        '''if value is not None and not isinstance(value, basestring):
            value = edit_string_for_tags([o.tag for o in value.select_related("tag")])
        '''

        output = [super(AutoCompleteModelWidget, self).render(name, value, attrs)]
        output.append(u'''
            <script>

                yepnope({
                    load:[
                        '%(static)sjs/jquery.js', '%(static)sjs/jquery-ui-1.8.15.custom.js'
                    ],
                    complete: function(){
                        jQuery(function(){
                            function split(val) {
                                return val.split(/\s*, \s*/);
                            }
                            function extractLast(term) {
                                return split(term).pop();
                            }
                            $('#%(id)s').autocomplete({
                                source: function(request, response) {
                                    $.getJSON('%(uri)s', {
                                        term: extractLast(request.term)
                                    }, response);
                                },
                                search: function() {
                                    // custom minLength
                                    var term = extractLast(this.value);
                                    if (term.length < %(length)s) {
                                        return false;
                                    }
                                },
                                focus: function() {
                                    // prevent value inserted on focus
                                    return false;
                                },
                                select: function(event, ui) {
                                    var terms = split( this.value );
                                    // remove the current input
                                    terms.pop();
                                    // add the selected item
                                    terms.push( ui.item.value );
                                    // add placeholder to get the comma-and-space at the end
                                    terms.push("");
                                    this.value = terms.join(", ");
                                    return false;
                                }
                            });
                        });
                    }
                });

            </script>
        ''' %  (self.options))

        return mark_safe(u''. join(output))


class AutoCompleteTagWidget(widgets.TextInput):
    '''
    Usage:
    tags = TagField(widget=AutoCompleteTagWidget(attrs={'app': 'your application name', 'model': 'your model', 'length': 2}), required=False)
    '''
    def __init__(self, *args, **kwargs):
        super(AutoCompleteTagWidget, self).__init__(*args, **kwargs)
        self.attrs = kwargs.get('attrs', {})
        self.length = self.attrs.get('length', '2') # default to 2 letters
        if self.attrs.get('model') and self.attrs.get('app') not in EMPTY_VALUES:
            self.model = get_model(self.attrs.get('app'), self.attrs.get('model'))
        else:
            pass

    class Media:
        css = {'all': ('%scss/autocomplete.css' % settings.THEIRRY_MEDIA_URL,)}

    def render(self, name, value, attrs=None):
        self.options = {
            'id': attrs['id'], 'tag_lookup': reverse('tag_lookup'),
            'length': self.length, 'static': settings.THEIRRY_MEDIA_URL,
        }

        if value in EMPTY_VALUES or len(value) == 0:
            value = ''
        else:
            complete_list = list()

            if isinstance(value, QuerySet):
                for v in value:
                    complete_list.append(v.tag.name)
                value = ', '.join(complete_list)

            if isinstance(value, unicode):
                pass

        output = [super(AutoCompleteTagWidget, self).render(name, value, attrs)]
        output.append(u'''
            <script>
                yepnope({
                    load:[
                       '%(static)sjs/jquery.js', '%(static)sjs/jquery-ui-1.8.15.custom.js'
                    ],
                    complete: function(){
                        jQuery(function(){

                            function split(val) {
                                return val.split(/\s*, \s*/);
                            }

                            function extractLast(term) {
                                return split(term).pop();
                            }
                            $('#%(id)s').autocomplete({
                                source: function(request, response) {
                                    $.getJSON('%(tag_lookup)s', {
                                        term: extractLast(request.term)
                                    }, response);
                                },
                                search: function() {
                                    // custom minLength
                                    var term = extractLast(this.value);
                                    if (term.length < %(length)s) {
                                        return false;
                                    }
                                },
                                focus: function() {
                                    // prevent value inserted on focus
                                    return false;
                                },
                                select: function(event, ui) {
                                    var terms = split( this.value );
                                    // remove the current input
                                    terms.pop();
                                    // add the selected item
                                    terms.push( ui.item.value );
                                    // add placeholder to get the comma-and-space at the end
                                    terms.push("");
                                    this.value = terms.join(", ");
                                    return false;
                                }
                            });

                        });
                    }
                });
            </script>
        ''' %  (self.options))

        return mark_safe(u''. join(output))


class USPhoneNumberMultiWidget(widgets.MultiWidget):
    """
    A Widget that splits US Phone number input into three  boxes.
    """
    def __init__(self,attrs=None):
        widgets = (
            TextInput(attrs={'size':'3','maxlength':'3', 'class':'phone'}),
            TextInput(attrs={'size':'3','maxlength':'3', 'class':'phone'}),
            TextInput(attrs={'size':'4','maxlength':'4', 'class':'phone'}),
        )
        super(USPhoneNumberMultiWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split('-')
        return [None,None,None]

    def value_from_datadict(self, data, files, name):
        values = super(USPhoneNumberMultiWidget, self).value_from_datadict(data, files, name)
        return u'%s-%s-%s' % values


class SSNInputWidget(widgets.TextInput):
    '''Renders United States SSN as xxx-xx-xxxx'''

    def render(self, name, value, attrs=None):
        if value and len(value) == 9:
            value = "%s-%s-%s" % (value[:3], value[3:5], value[5:])
        return super(SSNInputWidget, self).render(name, value, attrs)


class GenericWidget(widgets.HiddenInput):
    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        super(GenericWidget, self).__init__(attrs)
        '''
        Look for select attributes to override default
        generic = GenericField(widget=GenericWidget(attrs={'app': 'your application name', 'model': 'your module', 'pk': 'custom id function'}))
        '''
        self.attrs = attrs
        if self.attrs.get('module') and self.attrs.get('app') not in EMPTY_VALUES:
            self.model = get_model(self.attrs.get('app'), self.attrs.get('module'))
        self.fk = self.attrs.get('pk', create_uuid())

    def render(self, name, value, attrs=None, choices=()):
        '''
        call initial to set the foreign key
        '''
        if value:
            self.fk = value
        self.options = {
            "app": self.model._meta.app_label, 'module': self.model._meta.module_name,
            'fk': self.fk
        }
        output = list()
        output.append(u'''
            <div style='display:none'><input type='hidden' id='gen_app' name='gen_app' value='%(app)s' />
            <input type='hidden' id='gen_module' name='gen_module' value='%(module)s' />
            <input type='hidden' id='gen_fk_app' name='gen_fk_app' value='%(fk)s' /></div>'''
            % (self.options))
        return mark_safe(u''.join(output))


class DisplayOnlyWidget(widgets.HiddenInput):
    '''
    This extends the HiddenWidget and displays
    the info (value) contained in the input as
    text or (html)
    '''
    def __init__(self, foreign_object, *args, **kwargs):
        self.foreign_object = foreign_object
        # default to displaying the primary key
        self.field = 'id'
        self.attrs = kwargs.get('attrs', {})
        self.field = self.attrs.get('field', None)
        super(DisplayOnlyWidget, self).__init__()

    def render(self, name, value, attrs=None):
        if self.foreign_object is not None:
            display = '%s' % self.foreign_object.__dict__[self.field]
            return super(DisplayOnlyWidget, self).render(name, value, attrs) + mark_safe(display)
        else:
            return "None"