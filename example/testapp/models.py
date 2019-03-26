from __future__ import unicode_literals

from django.db import models
from django.db.models import Model
from django.db.models.query import Q
from django.contrib.auth.models import Group

from django.utils.translation import ugettext_lazy as _

# Create your models here.

class SomeObject(Model):
    name = models.CharField(max_length=80,verbose_name=_("Name"))

    def __unicode__(self):
        return _("Object: %s") % self.name

    class Meta:
        verbose_name = _("Some Object")
        verbose_name_plural = _("Some Objects")

class SomeChild(Model):
    parent = models.ForeignKey(SomeObject,on_delete=models.CASCADE,verbose_name=_("Parent"), related_name='children')
    name = models.CharField(max_length=80,verbose_name=_("Name"))

    def __unicode__(self):
        return _("Child: %s") % self.name

    class Meta:
        verbose_name = _("Some Child")
        verbose_name_plural = _("Some Childs")
