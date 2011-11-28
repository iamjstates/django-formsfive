#!/usr/bin/env python
import formsfive as forms
from datetime import datetime

class TextForm(forms.Form):
	text = forms.CharField(label='Sample Text Input', placeholder='Test the Placeholder')
	pw = forms.CharField(widget=forms.PasswordInput, placeholder='Enter Password')
	hide = forms.CharField(widget=forms.HiddenInput())
	date = forms.DateTimeField()
	time = forms.TimeField()
	query = forms.CharField(widget=forms.SearchInput)
	color = forms.CharField(widget=forms.ColorInput)
	num = forms.DecimalField(widget=forms.NumberInput(attrs={'step': 12}))
	range_ = forms.DecimalField(widget=forms.RangeInput)
	ds = forms.DateTimeField(initial=datetime.now(), widget=forms.SplitDateTimeWidget)
	dt = forms.DateTimeField(initial=datetime.now(), widget=forms.DateTimeLocalInput)