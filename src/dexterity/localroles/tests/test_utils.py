# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from ..testing import DLR_PROFILE_FUNCTIONAL
from ..utils import add_fti_configuration, fti_configuration
localroles_config = {
    u'private': {'raptor': {'roles': ('Editor', 'Contributor')}, 'cavemans': {'roles': ('Reader', )}},
    u'published': {'hunters': {'roles': ('Reader',)}, 'dina': {'roles': ('Editor',)}}}


class TestUtils(unittest.TestCase):

    layer = DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestUtils, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_fti_configuration(self):
        self.portal.invokeFactory('Document', 'doc')
        item = self.portal['doc']
        self.assertEqual(fti_configuration(item), {})
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        self.assertEqual(fti_configuration(item), {})
        add_fti_configuration('testingtype', localroles_config)
        self.assertEqual(fti_configuration(item)['static_config'], localroles_config)

    def test_add_fti_configuration(self):
        add_fti_configuration('testingtype', localroles_config)
        self.assertEqual(self.portal.portal_types.testingtype.localroles['static_config'], localroles_config)
        add_fti_configuration('testingtype', {})
        self.assertEqual(self.portal.portal_types.testingtype.localroles['static_config'], localroles_config)
        add_fti_configuration('testingtype', {}, force=True)
        self.assertEqual(self.portal.portal_types.testingtype.localroles['static_config'], {})
        self.assertEqual(add_fti_configuration('unknown', {}), "The portal type 'unknown' doesn't exist")
