from django.test import TestCase as _TestCase
from django.test import Client

import unittest
import mock

import re
import json

import os

from django.core.exceptions import ValidationError

import logging

from authenticated_signals.signals import *


class TestCase(_TestCase):
    if not hasattr(_TestCase,'assertRegex'):
        assertRegex = _TestCase.assertRegexpMatches
    if not hasattr(_TestCase,'assertNotRegex'):
        assertNotRegex = _TestCase.assertNotRegexpMatches

class TestBase(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User, Group, Permission
        from django.contrib import auth
        import testapp
        from django.contrib.contenttypes.models import ContentType
        from django.db.models import Model

        self.user = User.objects.create(username="test",is_active=True,is_staff=True)
        self.user.set_password("test")
        self.user.save()
        self.group = Group.objects.create(name="some")
        self.group.save()

        for cn in dir(auth.models):
            c = getattr(auth.models,cn)
            if isinstance(c,type) and c is not Model and issubclass(c,Model) and not c._meta.abstract and c._meta.app_label == 'auth':
                for cc in ['add','change','delete']:
                    self.group.permissions.add(
                        Permission.objects.get(
                            content_type=ContentType.objects.get(app_label=c._meta.app_label,model=c._meta.model_name),
                            codename='%s_%s' % (cc,c._meta.model_name),
                        )
                    )

        for cn in dir(testapp.models):
            c = getattr(testapp.models,cn)
            if isinstance(c,type) and c is not Model and issubclass(c,Model) and not c._meta.abstract and c._meta.app_label == 'testapp':
                for cc in ['add','change','delete']:
                    self.group.permissions.add(
                        Permission.objects.get(
                            content_type=ContentType.objects.get(app_label=c._meta.app_label,model=c._meta.model_name),
                            codename='%s_%s' % (cc,c._meta.model_name),
                        )
                    )

        self.group.user_set.add(self.user)

    def tearDown(self):
        from django.contrib.auth.models import User, Group, Permission
        User.objects.all().delete()
        Group.objects.all().delete()

class SignalsTest(TestBase):
    def test_1_check_add_signals(self):
        import testapp
        c = Client()
        c.login(username='test',password='test')
        self.pre_save_done = False
        def check_pre_save(sender, request=None, instance=None, *av, **kw):
            self.pre_save_done = True
            self.assertNotEqual(request, None)
            self.assertNotEqual(instance, None)
            self.assertEqual(instance.id, None)
        authenticated_pre_save.connect(check_pre_save, sender=testapp.models.SomeObject)

        c.post_save_done = False
        def check_post_save(sender, request=None, instance=None, created=None, *av, **kw):
            self.post_save_done = True
            self.assertNotEqual(request, None)
            self.assertNotEqual(instance, None)
            self.assertEqual(created, True)
        authenticated_post_save.connect(check_post_save, sender=testapp.models.SomeObject)

        response = c.post('/admin/testapp/someobject/add/',{
            'name':'test',
            'children-TOTAL_FORMS':2,
            'children-INITIAL_FORMS':0,
            'children-MIN_NUM_FORMS':0,
            'children-MAX_NUM_FORMS':1000,
            'children-0-name':'test1',
            'children-1-name':'test2',
        })

        self.assertEqual(response.status_code,302)

        authenticated_pre_save.disconnect(check_pre_save)
        authenticated_post_save.disconnect(check_post_save)

        self.assertEqual(self.pre_save_done, True)
        self.assertEqual(self.post_save_done, True)

    def test_2_check_update_signals(self):
        import testapp
        c = Client()
        c.login(username='test',password='test')

        response = c.post('/admin/testapp/someobject/add/',{
            'name':'test',
            'children-TOTAL_FORMS':2,
            'children-INITIAL_FORMS':0,
            'children-MIN_NUM_FORMS':0,
            'children-MAX_NUM_FORMS':1000,
            'children-0-name':'test1',
            'children-1-name':'test2',
            '_continue':'Save and continue editing',
        })

        self.assertEqual(response.status_code,302)
        change_loc = re.compile(r'.*admin/testapp/someobject/([^/]+)/change/.*')
        self.assertRegex(response['location'],change_loc)
        match = change_loc.match(response['location'])
        id = int(match.group(1))

        self.pre_save_done = False
        def check_pre_save(sender, request=None, instance=None, *av, **kw):
            self.pre_save_done = True
            self.assertNotEqual(request, None)
            self.assertNotEqual(instance, None)
            self.assertEqual(instance.id, id)
        authenticated_pre_save.connect(check_pre_save, sender=testapp.models.SomeObject)

        self.post_save_done = False
        def check_post_save(sender, request=None, instance=None, created=None, *av, **kw):
            self.post_save_done = True
            self.assertNotEqual(request, None)
            self.assertNotEqual(instance, None)
            self.assertEqual(created, False)
        authenticated_post_save.connect(check_post_save, sender=testapp.models.SomeObject)

        response = c.post('/admin/testapp/someobject/%s/change/' % id,{
            'name':'test',
            'children-TOTAL_FORMS':2,
            'children-INITIAL_FORMS':0,
            'children-MIN_NUM_FORMS':0,
            'children-MAX_NUM_FORMS':1000,
            'children-0-name':'test1',
            'children-1-name':'test2',
            '_continue':'Save and continue editing',
        })
        self.assertEqual(response.status_code,302)

        authenticated_pre_save.disconnect(check_pre_save)
        authenticated_post_save.disconnect(check_post_save)

        self.assertEqual(self.pre_save_done, True)
        self.assertEqual(self.post_save_done, True)

    def test_3_check_delete_signals(self):
        import testapp
        c = Client()
        c.login(username='test',password='test')

        response = c.post('/admin/testapp/someobject/add/',{
            'name':'test',
            'children-TOTAL_FORMS':2,
            'children-INITIAL_FORMS':0,
            'children-MIN_NUM_FORMS':0,
            'children-MAX_NUM_FORMS':1000,
            'children-0-name':'test1',
            'children-1-name':'test2',
            '_continue':'Save and continue editing',
        })

        self.assertEqual(response.status_code,302)
        change_loc = re.compile(r'.*admin/testapp/someobject/([^/]+)/change/.*')
        self.assertRegex(response['location'],change_loc)
        match = change_loc.match(response['location'])
        id = int(match.group(1))

        self.pre_delete_done = False
        def check_pre_delete(sender, request=None, instance=None, *av, **kw):
            self.pre_delete_done = True
            self.assertNotEqual(request, None)
            self.assertNotEqual(instance, None)
            self.assertEqual(instance.id, id)
        authenticated_pre_delete.connect(check_pre_delete, sender=testapp.models.SomeObject)

        self.post_delete_done = False
        def check_post_delete(sender, request=None, instance=None, *av, **kw):
            self.post_delete_done = True
            self.assertNotEqual(request, None)
            self.assertNotEqual(instance, None)
        authenticated_post_delete.connect(check_post_delete, sender=testapp.models.SomeObject)

        response = c.post('/admin/testapp/someobject/%s/delete/' % id,{
            'post':'yes',
        })
        self.assertEqual(response.status_code,302)

        authenticated_pre_delete.disconnect(check_pre_delete)
        authenticated_post_delete.disconnect(check_post_delete)

        self.assertEqual(self.pre_delete_done, True)
        self.assertEqual(self.post_delete_done, True)
