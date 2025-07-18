# -*- coding: utf-8 -*-

from dexterity.localroles import HAS_PLONE_6
from dexterity.localroles import testing
from dexterity.localroles.interfaces import IDexterityLocalRoles
from plone.browserlayer import utils

import unittest


if HAS_PLONE_6:
    from Products.CMFPlone.utils import get_installer


class TestSetup(unittest.TestCase):

    layer = testing.DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        portal = self.layer["portal"]
        if HAS_PLONE_6:
            self.installer = get_installer(portal)

    def test_product_installed(self):
        """Test if dexterity.localroles is installed with portal_quickinstaller."""
        if not HAS_PLONE_6:
            return
        self.assertTrue(self.installer.is_product_installed("dexterity.localroles"))

    def test_uninstall(self):
        """Test if dexterity.localroles is cleanly uninstalled."""
        if not HAS_PLONE_6:
            return
        self.installer.uninstall_product("dexterity.localroles")
        self.assertFalse(self.installer.is_product_installed("dexterity.localroles"))

    def test_browserlayer(self):
        """Test that IDexterityLocalRoles is registered."""
        if not HAS_PLONE_6:
            return
        self.assertIn(IDexterityLocalRoles, utils.registered_layers())
        self.installer.uninstall_product("dexterity.localroles")
        self.assertNotIn(IDexterityLocalRoles, utils.registered_layers())
