# -*- coding: utf-8 -*-
from dexterity.localroles.interfaces import ILocalRolesRelatedSearchUtility
from dexterity.localroles.testing import DLR_PROFILE_FUNCTIONAL
from dexterity.localroles.utility import ParentRelatedSearch
from dexterity.localroles.utility import ParentRelatedSearchWithPortal
from dexterity.localroles.utility import runRelatedSearch
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from zope.component import getUtility

import unittest


class TestRelatedSearchUtility(unittest.TestCase):

    layer = DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestRelatedSearchUtility, self).setUp()
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

    def test_get_objects(self):
        self.portal.invokeFactory("testingtype", "test")
        item = self.portal.get("test")
        utility = getUtility(ILocalRolesRelatedSearchUtility, "dexterity.localroles.related_parent_with_portal")
        self.assertIsInstance(utility, ParentRelatedSearchWithPortal)
        self.assertEqual(utility.get_objects(item), [self.portal])
        utility = getUtility(ILocalRolesRelatedSearchUtility, "dexterity.localroles.related_parent")
        self.assertIsInstance(utility, ParentRelatedSearch)
        self.assertEqual(utility.get_objects(item), [])

    def test_runRelatedSearch(self):
        self.portal.invokeFactory("testingtype", "test")
        item = self.portal.get("test")
        self.assertEqual(runRelatedSearch("error", item), [])
        self.assertEqual(runRelatedSearch("dexterity.localroles.related_parent_with_portal", item), [self.portal])
