# encoding: utf-8

from persistent.mapping import PersistentMapping
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import logout

from dexterity.localroles import testing

import unittest


class TestLocalRoles(unittest.TestCase):
    layer = testing.DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('testingtype', 'test')
        self.item = self.portal.get('test')
        self.content = api.content.create(container=self.portal,
                                          type='testingtype',
                                          id='testlocalroles',
                                          title='TestLocalRoles')
        config = {
            u'private': {
                'raptor': {'roles': ('Editor', 'Contributor')},
                'cavemans': {'roles': ('Reader', )}},
            u'published': {
                'hunters': {'roles': ('Reader', )},
                'wilma': {'roles': ('Editor', )}}}
        setattr(self.test_fti, 'localroles', PersistentMapping({'static_config': config}))

    def tearDown(self):
        api.content.delete(obj=self.content)
        setattr(self.test_fti, 'localroles', PersistentMapping())
        logout()

    @property
    def test_fti(self):
        return self.portal.portal_types.get('testingtype')

    def check_roles(self, test_roles, user=None, group=None):
        """Verify roles on the test item for a given username or groupname"""
        if user:
            roles = api.user.get_roles(username=user, obj=self.item)
            base_roles = ['Authenticated', 'Member']
        else:
            roles = api.group.get_roles(groupname=group, obj=self.item)
            base_roles = ['Authenticated']
        test_roles.extend(base_roles)
        self.assertItemsEqual(test_roles, roles)

    def test_roles_after_creation(self):
        self.assertEqual('private', api.content.get_state(obj=self.item))
        self.check_roles(['Reader'], group='cavemans')
        self.check_roles([], group='hunters')
        self.check_roles(['Reader'], user='fred')
        self.check_roles(['Reader'], user='wilma')
        self.check_roles(['Contributor', 'Editor'], user='raptor')
        self.check_roles([], user='t-rex')
        self.check_roles([], user='basic-user')

    def test_roles_after_transition(self):
        self.assertEqual('private', api.content.get_state(obj=self.item))
        api.content.transition(obj=self.item, transition='publish')
        self.assertEqual('published', api.content.get_state(obj=self.item))
        self.check_roles([], group='cavemans')
        self.check_roles(['Reader'], group='hunters')
        self.check_roles([], user='fred')
        self.check_roles(['Editor'], user='wilma')
        self.check_roles(['Reader'], user='raptor')
        self.check_roles(['Reader'], user='t-rex')
        self.check_roles([], user='basic-user')

        api.content.transition(obj=self.item, transition='retract')
        self.assertEqual('private', api.content.get_state(obj=self.item))
        self.check_roles(['Reader'], group='cavemans')
        self.check_roles([], group='hunters')
        self.check_roles(['Reader'], user='fred')
        self.check_roles(['Reader'], user='wilma')
        self.check_roles(['Contributor', 'Editor'], user='raptor')
        self.check_roles([], user='t-rex')
        self.check_roles([], user='basic-user')
