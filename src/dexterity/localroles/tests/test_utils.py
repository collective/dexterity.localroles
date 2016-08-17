# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from ..testing import DLR_PROFILE_FUNCTIONAL
from ..utils import (add_related_roles, del_related_roles, get_related_roles, set_related_roles, get_all_related_roles,
                     fti_configuration, add_fti_configuration)

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

    def test_add_related_roles(self):
        # nothing already stored
        add_related_roles(self.portal, 'fakeuid', 'raptor', [])
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'), {})
        # nothing already stored
        add_related_roles(self.portal, 'fakeuid', 'raptor', ['Reader'])
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'), {'raptor': set(['Reader'])})
        # adding to existing
        add_related_roles(self.portal, 'fakeuid', 'raptor', ['Reviewer'])
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'), {'raptor': set(['Reader', 'Reviewer'])})
        # adding another
        add_related_roles(self.portal, 'fakeuid', 't-rex', ['Reader'])
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'),
                             {'raptor': set(['Reader', 'Reviewer']), 't-rex': set(['Reader'])})

    def test_del_related_roles(self):
        # adding value
        add_related_roles(self.portal, 'fakeuid', 'raptor', ['Reader', 'Editor'])
        add_related_roles(self.portal, 'fakeuid', 't-rex', ['Reader'])
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'),
                             {'raptor': set(['Reader', 'Editor']), 't-rex': set(['Reader'])})
        self.assertSetEqual(del_related_roles(self.portal, 'fakeuid', 'raptor', ['Reader', 'Contributor']),
                            set(['Reader']))
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'),
                             {'raptor': set(['Editor']), 't-rex': set(['Reader'])})
        self.assertSetEqual(del_related_roles(self.portal, 'fakeuid', 'raptor', ['Editor']), set(['Editor']))
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'),
                             {'t-rex': set(['Reader'])})
        self.assertSetEqual(del_related_roles(self.portal, 'fakeuid', 't-rex', ['Reader']), set(['Reader']))
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'), {})

    def test_get_related_roles(self):
        # no key or no uid stored
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'), {})

    def test_get_all_related_roles(self):
        self.assertDictEqual(get_all_related_roles(self.portal), {})
        add_related_roles(self.portal, 'fakeuid', 'raptor', ['Reader', 'Editor'])
        self.assertDictEqual(dict(get_all_related_roles(self.portal)), {'raptor': set(['Editor', 'Reader'])})
        add_related_roles(self.portal, 'fakeuid', 't-rex', ['Reader'])
        self.assertDictEqual(dict(get_all_related_roles(self.portal)),
                             {'raptor': set(['Editor', 'Reader']), 't-rex': set(['Reader'])})
        add_related_roles(self.portal, 'fakeuid1', 't-rex', ['Reader'])
        self.assertDictEqual(dict(get_all_related_roles(self.portal)),
                             {'raptor': set(['Editor', 'Reader']), 't-rex': set(['Reader'])})

    def test_set_related_roles(self):
        # nothing already stored
        set_related_roles(self.portal, 'fakeuid', {'raptor': set(['Reader'])})
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'), {'raptor': set(['Reader'])})
        # replacing existing
        set_related_roles(self.portal, 'fakeuid', {'t-rex': set(['Reader'])})
        self.assertDictEqual(get_related_roles(self.portal, 'fakeuid'), {'t-rex': set(['Reader'])})

    def test_fti_configuration(self):
        self.portal.invokeFactory('Document', 'doc')
        item = self.portal['doc']
        self.assertEqual(fti_configuration(item), ({}, None))
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        self.assertEqual(fti_configuration(item), ({}, self.portal.portal_types.testingtype))
        add_fti_configuration('testingtype', localroles_config)
        self.assertEqual(fti_configuration(item),
                         ({'static_config': localroles_config}, self.portal.portal_types.testingtype))

    def test_add_fti_configuration(self):
        add_fti_configuration('testingtype', localroles_config)
        self.assertEqual(self.portal.portal_types.testingtype.localroles['static_config'], localroles_config)
        add_fti_configuration('testingtype', {})
        self.assertEqual(self.portal.portal_types.testingtype.localroles['static_config'], localroles_config)
        add_fti_configuration('testingtype', {}, force=True)
        self.assertEqual(self.portal.portal_types.testingtype.localroles['static_config'], {})
        self.assertEqual(add_fti_configuration('unknown', {}), "The portal type 'unknown' doesn't exist")
