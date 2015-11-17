# -*- coding: utf-8 -*-
import transaction
import unittest2 as unittest
from plone import api
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from ..browser.settings import LocalRoleConfigurationAdapter
from ..testing import DLR_PROFILE_FUNCTIONAL
from ..utils import add_fti_configuration, get_related_roles

localroles_config = {
    u'private': {'raptor': {'roles': ('Editor',),
                            'rel': "{'dexterity.localroles.related_parent':['Editor']}"},
                 'cavemans': {'roles': ('Reader', )}},
    u'published': {'raptor': {'roles': ('Reviewer',),
                              'rel': "{'dexterity.localroles.related_parent':['Reviewer']}"}},
}


class TestSubscriber(unittest.TestCase):

    layer = DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestSubscriber, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_related_change_on_transition(self):
        add_fti_configuration('testingtype', localroles_config)
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        # The parent is set by addition subscriber
        self.assertDictEqual(dict(get_related_roles(self.portal, item.UID())), {'raptor': set(['Editor'])})
        api.content.transition(obj=item, transition='publish')
        # The parent is changed
        self.assertDictEqual(dict(get_related_roles(self.portal, item.UID())), {'raptor': set(['Reviewer'])})

    def test_related_change_on_removal(self):
        add_fti_configuration('testingtype', localroles_config)
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        # The parent is set by addition subscriber
        self.assertDictEqual(dict(get_related_roles(self.portal, item.UID())), {'raptor': set(['Editor'])})
        api.content.transition(obj=item, transition='publish')
        api.content.delete(obj=item)
        # The parent is changed
        self.assertDictEqual(get_related_roles(self.portal, item.UID()), {})

    def test_related_change_on_addition(self):
        add_fti_configuration('testingtype', localroles_config)
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        # The parent is set
        self.assertDictEqual(dict(get_related_roles(self.portal, item.UID())), {'raptor': set(['Editor'])})

    def test_related_change_on_move(self):
        add_fti_configuration('testingtype', localroles_config)
        self.portal.invokeFactory('testingtype', 'test', title="Title")
        item = self.portal['test']
        # We need to commit here so that _p_jar isn't None and move will work
        transaction.savepoint(optimistic=True)
        # The parent is set by addition subscriber
        self.assertDictEqual(dict(get_related_roles(self.portal, item.UID())), {'raptor': set(['Editor'])})
        # We create a folder
        self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal['folder']
        self.assertDictEqual(get_related_roles(folder, item.UID()), {})
        # We move the item
        api.content.move(source=item, target=folder)
        # The old parent is changed
        self.assertDictEqual(get_related_roles(self.portal, item.UID()), {})
        # The new parent is changed
        self.assertDictEqual(dict(get_related_roles(folder, item.UID())), {'raptor': set(['Editor'])})
        item = folder['test']
        api.content.rename(obj=item, new_id='test1')

    def test_local_role_configuration_updated(self):
        class dummy(object):
            def __init__(self, fti):
                self.fti = fti
                self.context = self

        ctool = self.portal.portal_catalog
        fti = self.layer['portal'].portal_types.get('testingtype')
        dum = dummy(fti)
        cls = LocalRoleConfigurationAdapter(dum)
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        api.content.transition(obj=item, transition='submit')
        self.portal.invokeFactory('testingtype', 'test1')
        item1 = self.portal['test1']
        # Nothing is set !
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item1.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertNotIn('user:raptor', allowedRolesAndUsers)
        self.assertDictEqual(get_related_roles(self.portal, item1.UID()), {})
        # Adding a state
        setattr(cls, 'static_config',
                [{'state': 'private', 'value': 'raptor', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Editor']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item1.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:raptor', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, item1.UID())), {'raptor': set(['Editor'])})
        # Removing a state
        setattr(cls, 'static_config',
                [{'state': 'pending', 'value': 't-rex', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Editor']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item1.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertNotIn('user:raptor', allowedRolesAndUsers)
        self.assertDictEqual(get_related_roles(self.portal, item1.UID()), {})
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:t-rex', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, item.UID())), {'t-rex': set(['Editor'])})
        # Adding principal
        setattr(cls, 'static_config',
                [{'state': 'pending', 'value': 't-rex', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Editor']}"},
                 {'state': 'pending', 'value': 'raptor', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Editor']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:t-rex', allowedRolesAndUsers)
        self.assertIn('user:raptor', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, item.UID())), {'t-rex': set(['Editor']),
                                                                                'raptor': set(['Editor'])})
        # Removing principal
        setattr(cls, 'static_config',
                [{'state': 'pending', 'value': 't-rex', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Editor']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:t-rex', allowedRolesAndUsers)
        self.assertNotIn('user:raptor', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, item.UID())), {'t-rex': set(['Editor'])})
        # Removing roles, Adding and removing rel
        setattr(cls, 'static_config',
                [{'state': 'pending', 'value': 't-rex', 'roles': (),
                  'related': "{'dexterity.localroles.related_parent':['Reader']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertNotIn('user:t-rex', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, item.UID())), {'t-rex': set(['Reader'])})
