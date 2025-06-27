# -*- coding: utf-8 -*-

from dexterity.localroles import testing
from dexterity.localroles.interfaces import IDexterityLocalRoles
from plone.browserlayer import utils
from Products.CMFPlone.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):

    layer = testing.DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        portal = self.layer["portal"]
        self.installer = get_installer(portal)

    def test_product_installed(self):
        """Test if dexterity.localroles is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.is_product_installed("dexterity.localroles"))

    def test_uninstall(self):
        """Test if dexterity.localroles is cleanly uninstalled."""
        self.installer.uninstall_product("dexterity.localroles")
        self.assertFalse(self.installer.is_product_installed("dexterity.localroles"))

    def test_browserlayer(self):
        """Test that IDexterityLocalRoles is registered."""
        self.assertIn(IDexterityLocalRoles, utils.registered_layers())
        self.installer.uninstall_product("dexterity.localroles")
        self.assertNotIn(IDexterityLocalRoles, utils.registered_layers())
