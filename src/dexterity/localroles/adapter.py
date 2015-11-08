# encoding: utf-8

from zope.interface import implements

from borg.localrole.interfaces import ILocalRoleProvider

from utils import fti_configuration, get_state


class LocalRoleAdapter(object):
    """
        borg.localrole adapter to set localrole following type and state configuration
    """
    implements(ILocalRoleProvider)

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
            yield ('', ('', ))
            raise StopIteration
        for principal, roles_dic in state_config.items():
            yield (principal, tuple(roles_dic['roles']))

    @property
    def current_state(self):
        """Return the state of the current object"""
        return get_state(self.context)

    @property
    def config(self):
        fti_config = fti_configuration(self.context)
        return fti_config.get('static_config', {})
