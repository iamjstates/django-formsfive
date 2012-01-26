# Django Forms Five

A somewhat complete remap of django form to HTML5 form.

Modelform use widgets because you are not able to add extra field information at creation.  I believe this is a designed feature in django.core as line 199 in django.forms.fields generates wigdet_attribute only once. We have allowed you pass:


## Example - ModelForms
```
class TodoForm(forms.HTML5ModelForm):
    body = forms.CharField(label=_(u'Post or Story Body'), placeholder=_(u'listed'), required=True)
    sample = forms.IntegerField(max=25, min=10, step=5)

    class Meta:
        model = Todo
        exclude = ('slug', 'date')

    def __init__(self, *args, **kwargs):
        super(TodoForm, self).__init__(*args, **kwargs)
        self.fields['task'].widget.placeholder = _(u'A Task to do')
        self.fields['units'].widget.min = 0
        self.fields['units'].widget.max = 100
        self.fields['units'].widget.step = 5
```

## License

This software is licensed under the [New BSD License][BSD]. For more information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/