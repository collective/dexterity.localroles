# encoding: utf-8

from borg.localrole.interfaces import ILocalRoleProvider
from dexterity.localroles.utils import fti_configuration
from dexterity.localroles.utils import get_all_related_roles
from dexterity.localroles.utils import get_state
from zope.interface import implementer


@implementer(ILocalRoleProvider)
class LocalRoleAdapter(object):
    """
        borg.localrole adapter to set localrole following type and state configuration
    """

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal):
        """Grant permission for principal"""
        state_config = self.config.get(self.current_state)
        if not state_config:
            return []
        if not state_config.get(principal, []):
            return ()
        return tuple(state_config.get(principal)['roles'])

    def getAllRoles(self):
        """Grant permissions"""
        state_config = self.config.get(self.current_state)
        if not state_config:
            yield '', ('', )
            return
        for principal, roles_dic in state_config.items():
            yield principal, tuple(roles_dic['roles'])

    @property
    def current_state(self):
        """Return the state of the current object"""
        return get_state(self.context)

    @property
    def config(self):
        (fti_config, fti) = fti_configuration(self.context)
        return fti_config.get('static_config', {})


@implementer(ILocalRoleProvider)
class RelatedLocalRoleAdapter(object):
    """
        borg.localrole adapter to set related localroles following annotation
    """

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal):
        """Grant permission for principal"""
        if not self.related_roles.get(principal, []):
            return ()
        return tuple(self.related_roles.get(principal))

    def getAllRoles(self):
        """Grant permissions"""
        for principal, roles in self.related_roles.items():
            yield principal, tuple(roles)

    @property
    def related_roles(self):
        """Return a dict with principals and roles """
        return get_all_related_roles(self.context)
