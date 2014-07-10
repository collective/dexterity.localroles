# encoding: utf-8

from zope.schema.interfaces import ValidationError

from dexterity.localroles import _


class UnknownPrincipalError(ValidationError):
    __doc__ = _(u'Unknown principal')


class DuplicateEntryError(ValidationError):
    __doc__ = _(u'There is duplicate entries')
