from cms.models.pagemodel import Page
from cms.templatetags.cms_tags import get_site_id, _get_page_by_untyped_arg
from cms.test_utils.testcases import SettingsOverrideTestCase
from cms.test_utils.util.context_managers import SettingsOverride
from django.contrib.sites.models import Site
from django.core import mail
from unittest import TestCase


class TemplatetagTests(TestCase):
    def test_get_site_id_from_nothing(self):
        with SettingsOverride(SITE_ID=10):
            self.assertEqual(10, get_site_id(None))
        
    def test_get_site_id_from_int(self):
        self.assertEqual(10, get_site_id(10))
        
    def test_get_site_id_from_site(self):
        site = Site()
        site.id = 10
        self.assertEqual(10, get_site_id(site))
        
    def test_get_site_id_from_str_int(self):
        self.assertEqual(10, get_site_id('10'))
        
    def test_get_site_id_from_str(self):
        with SettingsOverride(SITE_ID=10):
            self.assertEqual(10, get_site_id("something"))


class TemplatetagDatabaseTests(SettingsOverrideTestCase):
    settings_overrides = {'CMS_MODERATOR': False}
    fixtures = ['twopages.json']
    
    def _getfirst(self):
        return Page.objects.get(pk=1)
    
    def _getsecond(self):
        return Page.objects.get(pk=2)
    
    def test_get_page_by_untyped_arg_none(self):
        control = self._getfirst()
        request = self.get_request('/')
        page = _get_page_by_untyped_arg(None, request, 1)
        self.assertEqual(page, control)
        
    def test_get_page_by_untyped_arg_page(self):
        control = self._getfirst()
        request = self.get_request('/')
        page = _get_page_by_untyped_arg(control, request, 1)
        self.assertEqual(page, control)
        
    def test_get_page_by_untyped_arg_reverse_id(self):
        second = self._getsecond()
        request = self.get_request('/')
        page = _get_page_by_untyped_arg("myreverseid", request, 1)
        self.assertEqual(page, second)
        
    def test_get_page_by_untyped_arg_dict(self):
        second = self._getsecond()
        request = self.get_request('/')
        page = _get_page_by_untyped_arg({'pk': 2}, request, 1)
        self.assertEqual(page, second)
        
    def test_get_page_by_untyped_arg_dict_fail_debug(self):
        with SettingsOverride(DEBUG=True):
            request = self.get_request('/')
            self.assertRaises(Page.DoesNotExist,
                _get_page_by_untyped_arg, {'pk': 3}, request, 1
            )
            self.assertEqual(len(mail.outbox), 0)
            
    def test_get_page_by_untyped_arg_dict_fail_nodebug(self):
        with SettingsOverride(DEBUG=False, MANAGERS=[("Jenkins", "tests@django-cms.org")]):
            request = self.get_request('/')
            page = _get_page_by_untyped_arg({'pk': 3}, request, 1)
            self.assertEqual(page, None)
            self.assertEqual(len(mail.outbox), 1)
    
    def test_get_page_by_untyped_arg_fail(self):
        request = self.get_request('/')
        self.assertRaises(TypeError, _get_page_by_untyped_arg, [], request, 1)