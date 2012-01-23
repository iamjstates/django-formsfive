#!/usr/bin/env python
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db import models, transaction, DEFAULT_DB_ALIAS
from datetime import datetime


class Todo(models.Model):
    slug = models.SlugField(max_length=300)
    date = models.DateTimeField(_(u'Date'), auto_now=False, auto_now_add=False)
    task = models.CharField(_(u'Task'), blank=True, max_length=300)
    units = models.PositiveIntegerField(_(u'Units'), blank=True, null=True)
    picture = models.FileField(_(u'Picture'), upload_to='picture', blank=True, null=True)

    class Meta:
        db_table = 'todo'
        get_latest_by = 'date'
        verbose_name = _(u'To Do')
        verbose_name_plural = _(u'To Do\'s')

    def __unicode__(self):
        return self.task

    @transaction.commit_on_success
    def save(self, force_insert=False, force_update=False, using=DEFAULT_DB_ALIAS):
        self.slug = slugify(self.task)
        self.date = datetime.now()
        super(Todo, self).save()
