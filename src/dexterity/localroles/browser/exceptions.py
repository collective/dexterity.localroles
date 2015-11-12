# encoding: utf-8

from zope.schema.interfaces import ValidationError

from dexterity.localroles import _


class UnknownPrincipalError(ValidationError):
    __doc__ = _(u'Unknown principal')


class DuplicateEntryError(ValidationError):
    __doc__ = _(u'There is duplicate entries')


class RelatedFormatError(ValidationError):
    __doc__ = _(u"Format must be as {'utility name':[roles],}")


class RoleNameError(ValidationError):
    __doc__ = _(u"A specified local role doesn't exist")


class UtilityNameError(ValidationError):
    __doc__ = _(u"A specified utility doesn't exist")
