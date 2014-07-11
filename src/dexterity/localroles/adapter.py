# encoding: utf-8

from borg.localrole.interfaces import ILocalRoleProvider
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility
from zope.interface import implements


class LocalRoleAdapter(object):
    implements(ILocalRoleProvider)

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal):
        """Grant permission for principal"""
        state_config = self.config.get(self.current_state)
        if not state_config:
            return []
        if self.is_user(principal):
            return tuple(state_config['users'].get(principal, []))
        else:
            return tuple(state_config['groups'].get(principal, []))

    @staticmethod
    def is_user(principal):
        return api.user.get(username=principal) is not None

    def getAllRoles(self):
        """Grant permissions"""
        state_config = self.config.get(self.current_state)
        if not state_config:
            yield ('', ('', ))
            raise StopIteration
        for key in ('users', 'groups'):
            for principal, roles in state_config.get(key).items():
                yield (principal, tuple(roles))

    @property
    def current_state(self):
        """Return the state of the current object"""
        return api.content.get_state(obj=self.context)

    @property
    def config(self):
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        return getattr(fti, 'localroleconfig', {})
