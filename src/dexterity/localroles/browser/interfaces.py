# encoding: utf-8

from zope.interface import Interface


class IWorkflowState(Interface):
    pass


class IRole(Interface):
    pass


class IPrincipal(Interface):
    pass


class ILocalRoleList(Interface):
    pass
