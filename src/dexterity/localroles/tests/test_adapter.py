# -*- coding: utf-8 -*-
from dexterity.localroles.testing import DLR_PROFILE_FUNCTIONAL
from dexterity.localroles.utils import add_fti_configuration
from ecreall.helpers.testing.search import BaseSearchTest
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import allowedRolesAndUsers

import unittest


localroles_config = {
    u"private": {
        "raptor": {
            "roles": ("Editor", "Contributor"),
            "rel": '{"dexterity.localroles.related_parent":["Editor"]}',
        },
        "cavemans": {"roles": ("Reader",)},
    },
    u"published": {
        "hunters": {
            "roles": ("Reader",),
            "rel": '{"dexterity.localroles.related_parent":["Reader"]}',
        },
        "wilma": {"roles": ("Editor",)},
    },
}


class TestAdapter(unittest.TestCase, BaseSearchTest):
    """Tests adapters"""

    layer = DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestAdapter, self).setUp()
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        add_fti_configuration("testingtype", localroles_config)

    def test_localroles_change_on_statechange(self):
        self.portal.invokeFactory("testingtype", "test")
        item = self.portal["test"]
        self.assertContainsSame(
            api.group.get_roles(groupname="cavemans", obj=item),
            ["Authenticated", "Reader"],
        )
        self.assertContainsSame(
            api.group.get_roles(groupname="hunters", obj=item), ["Authenticated"]
        )
        self.assertContainsSame(
            api.user.get_roles(username="fred", obj=item),
            ["Authenticated", "Member", "Reader"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="wilma", obj=item),
            ["Authenticated", "Member", "Reader"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="raptor", obj=item),
            ["Authenticated", "Member", "Contributor", "Editor"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="t-rex", obj=item), ["Authenticated", "Member"]
        )
        self.assertContainsSame(
            api.user.get_roles(username="basic-user", obj=item),
            ["Authenticated", "Member"],
        )
        workflow = getToolByName(self.portal, "portal_workflow")
        workflow.doActionFor(item, "publish")
        self.assertContainsSame(
            api.group.get_roles(groupname="cavemans", obj=item), ["Authenticated"]
        )
        self.assertContainsSame(
            api.group.get_roles(groupname="hunters", obj=item),
            ["Authenticated", "Reader"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="fred", obj=item), ["Authenticated", "Member"]
        )
        self.assertContainsSame(
            api.user.get_roles(username="wilma", obj=item),
            ["Authenticated", "Member", "Editor"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="raptor", obj=item),
            ["Authenticated", "Member", "Reader"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="t-rex", obj=item),
            ["Authenticated", "Member", "Reader"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="basic-user", obj=item),
            ["Authenticated", "Member"],
        )
        workflow.doActionFor(item, "retract")
        self.assertContainsSame(
            api.group.get_roles(groupname="cavemans", obj=item),
            ["Authenticated", "Reader"],
        )
        self.assertContainsSame(
            api.group.get_roles(groupname="hunters", obj=item), ["Authenticated"]
        )
        self.assertContainsSame(
            api.user.get_roles(username="fred", obj=item),
            ["Authenticated", "Member", "Reader"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="wilma", obj=item),
            ["Authenticated", "Member", "Reader"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="raptor", obj=item),
            ["Authenticated", "Member", "Contributor", "Editor"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="t-rex", obj=item), ["Authenticated", "Member"]
        )
        self.assertContainsSame(
            api.user.get_roles(username="basic-user", obj=item),
            ["Authenticated", "Member"],
        )

    def test_catalog(self):
        self.portal.invokeFactory("testingtype", "test")
        item = self.portal["test"]
        self.assertCanFind(item)
        ctool = self.portal.portal_catalog
        allowed_roles_and_users = ctool.getIndexDataForUID(
            "/".join(item.getPhysicalPath())
        )["allowedRolesAndUsers"]
        self.assertIn("user:cavemans", allowed_roles_and_users)
        self.assertNotIn("user:hunters", allowed_roles_and_users)
        self.assertNotIn("user:fred", allowed_roles_and_users)
        self.assertIn("user:raptor", allowed_roles_and_users)
        self.assertNotIn("user:t-rex", allowed_roles_and_users)
        self.assertNotIn("user:basic-user", allowed_roles_and_users)
        workflow = getToolByName(self.portal, "portal_workflow")
        workflow.doActionFor(item, "publish")
        self.assertEqual(allowedRolesAndUsers(item)(), ["Anonymous"])
        workflow.doActionFor(item, "retract")
        allowed_roles_and_users = allowedRolesAndUsers(item)()
        self.assertIn("user:cavemans", allowed_roles_and_users)
        self.assertNotIn("user:hunters", allowed_roles_and_users)
        self.assertNotIn("user:fred", allowed_roles_and_users)
        self.assertIn("user:raptor", allowed_roles_and_users)
        self.assertNotIn("user:t-rex", allowed_roles_and_users)
        self.assertNotIn("user:basic-user", allowed_roles_and_users)

    def test_related_localroles_change_on_statechange(self):
        self.portal.invokeFactory("Folder", "folder")
        folder = self.portal["folder"]
        # No related roles
        self.assertContainsSame(
            api.group.get_roles(groupname="cavemans", obj=folder), ["Authenticated"]
        )
        self.assertContainsSame(
            api.group.get_roles(groupname="hunters", obj=folder), ["Authenticated"]
        )
        self.assertContainsSame(
            api.user.get_roles(username="raptor", obj=folder),
            ["Authenticated", "Member"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="wilma", obj=folder),
            ["Authenticated", "Member"],
        )
        folder.invokeFactory("testingtype", "test")
        item = folder["test"]
        # Related roles after creation
        self.assertContainsSame(
            api.group.get_roles(groupname="cavemans", obj=folder), ["Authenticated"]
        )
        self.assertContainsSame(
            api.group.get_roles(groupname="hunters", obj=folder), ["Authenticated"]
        )
        self.assertContainsSame(
            api.user.get_roles(username="raptor", obj=folder),
            ["Authenticated", "Member", "Editor"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="wilma", obj=folder),
            ["Authenticated", "Member"],
        )
        api.content.transition(obj=item, transition="publish")
        # Related roles after publish
        self.assertContainsSame(
            api.group.get_roles(groupname="cavemans", obj=folder), ["Authenticated"]
        )
        self.assertContainsSame(
            api.group.get_roles(groupname="hunters", obj=folder),
            ["Authenticated", "Reader"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="raptor", obj=folder),
            ["Authenticated", "Member", "Reader"],
        )
        self.assertContainsSame(
            api.user.get_roles(username="wilma", obj=folder),
            ["Authenticated", "Member"],
        )
