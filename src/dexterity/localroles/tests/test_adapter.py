# -*- coding: utf-8 -*-
import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID
from ecreall.helpers.testing.search import BaseSearchTest

from ..testing import DLR_PROFILE_FUNCTIONAL
from ..utils import add_fti_configuration

localroles_config = {
    u'private': {'raptor': {'roles': ('Editor', 'Contributor'),
                            'rel': "{'dexterity.localroles.related_parent':['Editor']}"},
                 'cavemans': {'roles': ('Reader', )}},
    u'published': {'hunters': {'roles': ('Reader', ),
                               'rel': "{'dexterity.localroles.related_parent':['Reader']}"},
                   'wilma': {'roles': ('Editor', )}}}


class TestAdapter(unittest.TestCase, BaseSearchTest):
    """Tests adapters"""
    layer = DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestAdapter, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        add_fti_configuration('testingtype', localroles_config)

    def test_localroles_change_on_statechange(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        self.assertContainsSame(api.group.get_roles(groupname='cavemans', obj=item), ['Authenticated', 'Reader'])
        self.assertContainsSame(api.group.get_roles(groupname='hunters', obj=item), ['Authenticated'])
        self.assertContainsSame(api.user.get_roles(username='fred', obj=item),
                                ['Authenticated', 'Member', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='wilma', obj=item),
                                ['Authenticated', 'Member', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='raptor', obj=item),
                                ['Authenticated', 'Member', 'Contributor', 'Editor'])
        self.assertContainsSame(api.user.get_roles(username='t-rex', obj=item),
                                ['Authenticated', 'Member'])
        self.assertContainsSame(api.user.get_roles(username='basic-user', obj=item),
                                ['Authenticated', 'Member'])
        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.doActionFor(item, 'publish')
        self.assertContainsSame(api.group.get_roles(groupname='cavemans', obj=item), ['Authenticated'])
        self.assertContainsSame(api.group.get_roles(groupname='hunters', obj=item), ['Authenticated', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='fred', obj=item),
                                ['Authenticated', 'Member'])
        self.assertContainsSame(api.user.get_roles(username='wilma', obj=item),
                                ['Authenticated', 'Member', 'Editor'])
        self.assertContainsSame(api.user.get_roles(username='raptor', obj=item),
                                ['Authenticated', 'Member', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='t-rex', obj=item),
                                ['Authenticated', 'Member', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='basic-user', obj=item),
                                ['Authenticated', 'Member'])
        workflow.doActionFor(item, 'retract')
        self.assertContainsSame(api.group.get_roles(groupname='cavemans', obj=item), ['Authenticated', 'Reader'])
        self.assertContainsSame(api.group.get_roles(groupname='hunters', obj=item), ['Authenticated'])
        self.assertContainsSame(api.user.get_roles(username='fred', obj=item),
                                ['Authenticated', 'Member', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='wilma', obj=item),
                                ['Authenticated', 'Member', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='raptor', obj=item),
                                ['Authenticated', 'Member', 'Contributor', 'Editor'])
        self.assertContainsSame(api.user.get_roles(username='t-rex', obj=item),
                                ['Authenticated', 'Member'])
        self.assertContainsSame(api.user.get_roles(username='basic-user', obj=item),
                                ['Authenticated', 'Member'])

    def test_catalog(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        self.assertCanFind(item)
        ctool = self.portal.portal_catalog
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:cavemans', allowedRolesAndUsers)
        self.assertNotIn('user:hunters', allowedRolesAndUsers)
        self.assertNotIn('user:fred', allowedRolesAndUsers)
        self.assertIn('user:raptor', allowedRolesAndUsers)
        self.assertNotIn('user:t-rex', allowedRolesAndUsers)
        self.assertNotIn('user:basic-user', allowedRolesAndUsers)
        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.doActionFor(item, 'publish')
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertEqual(allowedRolesAndUsers, ['Anonymous'])
        workflow.doActionFor(item, 'retract')
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:cavemans', allowedRolesAndUsers)
        self.assertNotIn('user:hunters', allowedRolesAndUsers)
        self.assertNotIn('user:fred', allowedRolesAndUsers)
        self.assertIn('user:raptor', allowedRolesAndUsers)
        self.assertNotIn('user:t-rex', allowedRolesAndUsers)
        self.assertNotIn('user:basic-user', allowedRolesAndUsers)

    def test_related_localroles_change_on_statechange(self):
        self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal['folder']
        # No related roles
        self.assertContainsSame(api.group.get_roles(groupname='cavemans', obj=folder), ['Authenticated'])
        self.assertContainsSame(api.group.get_roles(groupname='hunters', obj=folder), ['Authenticated'])
        self.assertContainsSame(api.user.get_roles(username='raptor', obj=folder), ['Authenticated', 'Member'])
        self.assertContainsSame(api.user.get_roles(username='wilma', obj=folder), ['Authenticated', 'Member'])
        folder.invokeFactory('testingtype', 'test')
        item = folder['test']
        # Related roles after creation
        self.assertContainsSame(api.group.get_roles(groupname='cavemans', obj=folder), ['Authenticated'])
        self.assertContainsSame(api.group.get_roles(groupname='hunters', obj=folder), ['Authenticated'])
        self.assertContainsSame(api.user.get_roles(username='raptor', obj=folder),
                                ['Authenticated', 'Member', 'Editor'])
        self.assertContainsSame(api.user.get_roles(username='wilma', obj=folder),
                                ['Authenticated', 'Member'])
        api.content.transition(obj=item, transition='publish')
        # Related roles after publish
        self.assertContainsSame(api.group.get_roles(groupname='cavemans', obj=folder), ['Authenticated'])
        self.assertContainsSame(api.group.get_roles(groupname='hunters', obj=folder), ['Authenticated', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='raptor', obj=folder),
                                ['Authenticated', 'Member', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='wilma', obj=folder),
                                ['Authenticated', 'Member'])
