# encoding: utf-8

from zope.interface import Interface, Attribute


class IWorkflowState(Interface):
    pass


class IRole(Interface):
    pass


class IPrincipal(Interface):
    pass


class ILocalRoleList(Interface):
    pass


class ILocalRoleListUpdatedEvent(Interface):
    """
        A LocalRoleList field has been modified
    """

    fti = Attribute("The Dexterity FTI")

    field = Attribute("The field name that has been changed")

    old_value = Attribute("The value of the field before modification")

    new_value = Attribute("The value of the field after modification")
