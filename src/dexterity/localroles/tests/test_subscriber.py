# -*- coding: utf-8 -*-
import transaction
import unittest2 as unittest
from zope import event
from zope.lifecycleevent import ObjectModifiedEvent
from plone import api
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from ..browser.settings import LocalRoleConfigurationAdapter
from ..testing import DLR_PROFILE_FUNCTIONAL
from ..utils import add_fti_configuration, get_related_roles

localroles_config = {
    u'private': {'raptor': {'roles': ('Editor',),
                            'rel': "[{'utility':'dexterity.localroles.related_parent','roles':['Editor']}]"},
                 'cavemans': {'roles': ('Reader', )}},
    u'published': {'raptor': {'roles': ('Reviewer',),
                              'rel': "[{'utility':'dexterity.localroles.related_parent','roles':['Reviewer']}]"}},
}


class TestSubscriber(unittest.TestCase):

    layer = DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestSubscriber, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_local_role_configuration_updated(self):
        add_fti_configuration('testingtype', localroles_config)
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        ctool = self.portal.portal_catalog
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:cavemans', allowedRolesAndUsers)
        self.assertIn('user:raptor', allowedRolesAndUsers)

        class dummy(object):
            def __init__(self, fti):
                self.fti = fti
                self.context = self

        fti = self.layer['portal'].portal_types.get('testingtype')
        dum = dummy(fti)
        cls = LocalRoleConfigurationAdapter(dum)
        del localroles_config['private']['cavemans']
        add_fti_configuration('testingtype', localroles_config)
        event.notify(ObjectModifiedEvent(cls))
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertNotIn('user:cavemans', allowedRolesAndUsers)
        self.assertIn('user:raptor', allowedRolesAndUsers)

    def test_related_change_on_transition(self):
        add_fti_configuration('testingtype', localroles_config)
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        # The parent is set by addition subscriber
        self.assertDictEqual(get_related_roles(self.portal, item.UID()), {'raptor': set(['Editor'])})
        api.content.transition(obj=item, transition='publish')
        # The parent is changed
        self.assertDictEqual(get_related_roles(self.portal, item.UID()), {'raptor': set(['Reviewer'])})

    def test_related_change_on_removal(self):
        add_fti_configuration('testingtype', localroles_config)
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        # The parent is set by addition subscriber
        self.assertDictEqual(get_related_roles(self.portal, item.UID()), {'raptor': set(['Editor'])})
        api.content.transition(obj=item, transition='publish')
        api.content.delete(obj=item)
        # The parent is changed
        self.assertDictEqual(get_related_roles(self.portal, item.UID()), {})

    def test_related_change_on_addition(self):
        add_fti_configuration('testingtype', localroles_config)
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        # The parent is set
        self.assertDictEqual(get_related_roles(self.portal, item.UID()), {'raptor': set(['Editor'])})

    def test_related_change_on_move(self):
        add_fti_configuration('testingtype', localroles_config)
        self.portal.invokeFactory('testingtype', 'test', title="Title")
        item = self.portal['test']
        # We need to commit here so that _p_jar isn't None and move will work
        transaction.savepoint(optimistic=True)
        # The parent is set by addition subscriber
        self.assertDictEqual(get_related_roles(self.portal, item.UID()), {'raptor': set(['Editor'])})
        # We create a folder
        self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal['folder']
        self.assertDictEqual(get_related_roles(folder, item.UID()), {})
        # We move the item
        api.content.move(source=item, target=folder)
        # The old parent is changed
        self.assertDictEqual(get_related_roles(self.portal, item.UID()), {})
        # The new parent is changed
        self.assertDictEqual(get_related_roles(folder, item.UID()), {'raptor': set(['Editor'])})
