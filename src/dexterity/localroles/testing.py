# -*- coding: utf-8 -*-
import dexterity.localroles
import pkg_resources
from plone import api
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import ploneSite
from plone.testing import z2, zca

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_PA_CONTENTTYPES = False
else:
    HAS_PA_CONTENTTYPES = True

DLR_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                           package=dexterity.localroles,
                           name='DLR_ZCML')

DLR_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, DLR_ZCML),
                               name='DLR_Z2')


class DLRLayer(PloneWithPackageLayer):

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        super(DLRLayer, self).setUpPloneSite(portal)

        # Plone 5 support
        if HAS_PA_CONTENTTYPES:
            self.applyProfile(portal, 'plone.app.contenttypes:default')


DLR = DLRLayer(
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
                    if not api.user.get(username=user):
                        api.user.create(username=user, email='flint@stone.be')
                    api.group.add_user(groupname=group_id, username=user)
            if not api.user.get(username='basic-user'):
                api.user.create(username='basic-user', email='flint@stone.be')


DLR_PROFILE_FUNCTIONAL = DLRFunctionalTesting(
    bases=(DLR,), name="DLR_PROFILE_FUNCTIONAL")

DLR_ROBOT_TESTING = DLRFunctionalTesting(
    bases=(
        DLR,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="DLR_ROBOT_TESTING",
)
