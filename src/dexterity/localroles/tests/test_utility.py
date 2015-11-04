# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope.component import getUtility
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from ..utility import ParentRelatedSearch, runRelatedSearch
from ..interfaces import ILocalRolesRelatedSearchUtility
from ..testing import DLR_PROFILE_FUNCTIONAL


class TestRelatedSearchUtility(unittest.TestCase):

    layer = DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestRelatedSearchUtility, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_get_objects(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal.get('test')
        utility = getUtility(ILocalRolesRelatedSearchUtility, 'dexterity.localroles.related_parent')
        self.assertIsInstance(utility, ParentRelatedSearch)
        self.assertEqual(utility.get_objects(item), [self.portal])

    def test_runRelatedSearch(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal.get('test')
        self.assertEqual(runRelatedSearch('error', item), [])
        self.assertEqual(runRelatedSearch('dexterity.localroles.related_parent', item),
                         [self.portal])
