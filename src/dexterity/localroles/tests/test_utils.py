# -*- coding: utf-8 -*-
from dexterity.localroles.testing import DLR_PROFILE_FUNCTIONAL
from dexterity.localroles.utils import add_fti_configuration
from dexterity.localroles.utils import add_related_roles
from dexterity.localroles.utils import del_related_roles
from dexterity.localroles.utils import fti_configuration
from dexterity.localroles.utils import get_all_related_roles
from dexterity.localroles.utils import get_related_roles
from dexterity.localroles.utils import set_related_roles
from dexterity.localroles.utils import update_roles_in_fti
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME

import unittest2 as unittest


localroles_config = {
    u'private': {'raptor': {'roles': ('Editor', 'Contributor'),
                            'rel': "{'dexterity.localroles.related_parent': ('Reader',)}"},
                 'cavemans': {'roles': ('Reader', )}},
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
        self.assertEqual(fti_configuration(portal_type='testingtype'),
                         ({'static_config': localroles_config}, self.portal.portal_types.testingtype))

    def test_add_fti_configuration(self):
        add_fti_configuration('testingtype', localroles_config)
        self.assertEqual(self.portal.portal_types.testingtype.localroles['static_config'], localroles_config)
        add_fti_configuration('testingtype', {})
        self.assertEqual(self.portal.portal_types.testingtype.localroles['static_config'], localroles_config)
        add_fti_configuration('testingtype', {}, force=True)
        self.assertEqual(self.portal.portal_types.testingtype.localroles['static_config'], {})
        self.assertEqual(add_fti_configuration('unknown', {}), "The portal type 'unknown' doesn't exist")

    def test_update_roles_in_fti(self):
        # we add something
        update_roles_in_fti('testingtype', localroles_config)
        dic = self.portal.portal_types.testingtype.localroles['static_config']
        self.assertListEqual(dic['private']['raptor']['roles'], ['Editor', 'Contributor'])
        self.assertEqual(dic['private']['raptor']['rel'], "{'dexterity.localroles.related_parent': ('Reader',)}")
        self.assertListEqual(dic['private']['cavemans']['roles'], ['Reader'])
        self.assertEqual(dic['private']['cavemans']['rel'], "")
        self.assertListEqual(dic['published']['hunters']['roles'], ['Reader'])
        self.assertListEqual(dic['published']['dina']['roles'], ['Editor'])
        update_roles_in_fti('testingtype', {'private': {'cavemans': {'roles': ('Reviewer',)}}})
        self.assertListEqual(dic['private']['raptor']['roles'], ['Editor', 'Contributor'])
        self.assertEqual(dic['private']['raptor']['rel'], "{'dexterity.localroles.related_parent': ('Reader',)}")
        self.assertListEqual(dic['private']['cavemans']['roles'], ['Reader', 'Reviewer'])
        self.assertEqual(dic['private']['cavemans']['rel'], "")
        self.assertListEqual(dic['published']['hunters']['roles'], ['Reader'])
        self.assertListEqual(dic['published']['dina']['roles'], ['Editor'])
        update_roles_in_fti('testingtype', {'private': {'cavemans': {'roles': ('Reviewer',)},
                                                        'dina': {'roles': ('Reader', 'Reviewer')},
                                                        'raptor': {'rel': "{'a_utility': ('Reader',)}"}},
                                            'published': {'hunters': {'roles': ('Reviewer',)},
                                                          'dina': {'roles': ('Reviewer', )}}})
        self.assertListEqual(dic['private']['raptor']['roles'], ['Editor', 'Contributor'])
        self.assertEqual(dic['private']['raptor']['rel'], "{'a_utility': ('Reader',)}")
        self.assertListEqual(dic['private']['cavemans']['roles'], ['Reader', 'Reviewer'])
        self.assertListEqual(dic['private']['dina']['roles'], ['Reader', 'Reviewer'])
        self.assertListEqual(dic['published']['hunters']['roles'], ['Reader', 'Reviewer'])
        self.assertListEqual(dic['published']['dina']['roles'], ['Editor', 'Reviewer'])
        # we remove something
        update_roles_in_fti('testingtype', {'private': {'cavemans': {'roles': ('Reviewer',)},
                                                        'dina': {'roles': ('Reader', 'Reviewer')},
                                                        'raptor': {'rel': "{'a_utility': ('Reader',)}"}},
                                            'published': {'hunters': {'roles': ('Reviewer',)},
                                                          'dina': {'roles': ('Reviewer', )}}}, action='rem')
        self.assertListEqual(dic['private']['raptor']['roles'], ['Editor', 'Contributor'])
        self.assertEqual(dic['private']['raptor']['rel'], "")
        self.assertListEqual(dic['private']['cavemans']['roles'], ['Reader', ])
        self.assertEqual(dic['private']['cavemans']['rel'], "")
        self.assertNotIn('dina', dic['private'])
        self.assertListEqual(dic['published']['hunters']['roles'], ['Reader'])
        self.assertListEqual(dic['published']['dina']['roles'], ['Editor'])
        update_roles_in_fti('testingtype', {u'private': {'cavemans': {'roles': ('Reader', 'Reviewer')},
                                                         'raptor': {'roles': ('Editor', 'Contributor')}}}, action='rem')
        self.assertNotIn('private', dic)
        update_roles_in_fti('testingtype', {u'published': {'hunters': {'roles': ('Reader',)},
                                                           'dina': {'roles': ('Editor',)}}}, action='rem')
        self.assertNotIn('published', dic)
        self.assertEqual(len(self.portal.portal_types.testingtype.localroles['static_config']), 0)
