#!/usr/bin/env python

EMPTY_VALUES = (None, '', 'NoneType', False)

UNIVERSAL = ('autocomplete', 'required')

TEXT_SEARCH = (
	'dirname', 'list', 'maxlength',
    'pattern', 'placeholder', 'readonly',
    'size', 'spellcheck')

EMAIL = ('multiple')

SELECT = ('multiple', 'name', 'size')

PASSWORD = ('maxlength', 'pattern', 'list', 'placeholder', 'readonly')

TIME_NUMERIC = ('min', 'max', 'readonly', 'step', 'list')

RANGE = ('min', 'max', 'list', 'step')

CHOICE = ('value', 'choices', 'check_test')

WIDGETS = ('is_required', 'autofocus', 'disabled', 'placeholder', 'pattern', 'spellcheck')