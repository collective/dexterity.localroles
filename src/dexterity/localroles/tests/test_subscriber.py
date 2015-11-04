# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope import event
from zope.lifecycleevent import ObjectModifiedEvent
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from ..browser.settings import LocalRoleConfigurationAdapter
from ..testing import DLR_PROFILE_FUNCTIONAL
from ..utils import add_fti_configuration

localroles_config = {
    u'private': {'raptor': {'roles': ('Editor',)}, 'cavemans': {'roles': ('Reader', )}},
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
