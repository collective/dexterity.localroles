# encoding: utf-8

from borg.localrole.interfaces import ILocalRoleProvider
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility, ComponentLookupError
from zope.interface import implements
from Products.CMFCore.WorkflowCore import WorkflowException


class LocalRoleAdapter(object):
    implements(ILocalRoleProvider)

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal):
        """Grant permission for principal"""
        state_config = self.config.get(self.current_state)
        if not state_config:
            return []
        return tuple(state_config.get(principal, []))

    def getAllRoles(self):
        """Grant permissions"""
        state_config = self.config.get(self.current_state)
        if not state_config:
            yield ('', ('', ))
            raise StopIteration
        for principal, roles in state_config.items():
            yield (principal, tuple(roles))

    @property
    def current_state(self):
        """Return the state of the current object"""
        try:
            return api.content.get_state(obj=self.context)
        except (WorkflowException, api.portal.CannotGetPortalError):
            return None

    @property
    def config(self):
        try:
            fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        except ComponentLookupError:
            # when deleting site
            return {}
        return getattr(fti, 'localroleconfig', {})
