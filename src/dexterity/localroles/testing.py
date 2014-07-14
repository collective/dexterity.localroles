# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing import ploneSite
from plone import api
import dexterity.localroles


DLR_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                           package=dexterity.localroles,
                           name='DLR_ZCML')

DLR_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, DLR_ZCML),
                               name='DLR_Z2')

DLR = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=dexterity.localroles,
    additional_z2_products=(),
    gs_profile_id='dexterity.localroles:testing',
    name="DLR")


class DLRFunctionalTesting(FunctionalTesting):

    def setUp(self):
        super(DLRFunctionalTesting, self).setUp()
        with ploneSite() as portal:
            groups_tool = portal.portal_groups
            groups = {'hunters': ('raptor', 't-rex'), 'cavemans': ('fred', 'wilma')}
            for group_id in groups:
                if group_id not in groups_tool.getGroupIds():
                    groups_tool.addGroup(group_id)
                for user in groups[group_id]:
                    api.user.create(username=user, email='flint@stone.be')
                    api.group.add_user(groupname=group_id, username=user)


DLR_PROFILE_FUNCTIONAL = DLRFunctionalTesting(
    bases=(DLR, ), name="DLR_PROFILE_FUNCTIONAL")