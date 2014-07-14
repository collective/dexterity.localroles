# -*- coding: utf-8 -*-
import unittest2 as unittest
from mock import Mock

from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID
from ecreall.helpers.testing.base import BaseTest

from ..testing import DLR_PROFILE_FUNCTIONAL
from ..utils import add_fti_configuration

localroles_config = {
    u'private': {'raptor': ('Editor', 'Contributor'), 'cavemans': ('Reader', )},
    u'published': {'hunters': ('Reader',), 'dina': ('Editor',)}}


class TestAdapter(unittest.TestCase, BaseTest):
    """Tests adapters"""
    layer = DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestAdapter, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        api.content.get_state = Mock(return_value='private')
        add_fti_configuration('testingtype', localroles_config)

    def test_localroles_change_on_statechange(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = self.portal['test']
        self.assertContainsSame(api.group.get_roles(groupname='cavemans', obj=item), ['Authenticated', 'Reader'])
        self.assertContainsSame(api.user.get_roles(username='raptor', obj=item),
                                ['Authenticated', 'Contributor', 'Editor', 'Member'])
        self.assertContainsSame(api.user.get_roles(username='t-rex', obj=item),
                                ['Authenticated', 'Member'])
        #to be continued
        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.doActionFor(item, 'publish')

        workflow.doActionFor(item, 'retract')
