# -*- coding: utf-8 -*-
"""Example."""
from .interfaces import ILocalRolesRelatedSearchUtility
from Acquisition import aq_inner
from Acquisition import aq_parent
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements


class ParentRelatedSearch(object):
    """ Example related search. """

    implements(ILocalRolesRelatedSearchUtility)

    def get_objects(self, obj):
        """ Return the parent. """
        return [aq_parent(aq_inner(obj))]


def runRelatedSearch(utility, obj):
    """ Run the related search and return the result """
    try:
        util = getUtility(ILocalRolesRelatedSearchUtility, utility)
    except ComponentLookupError:
        return []
    return util.get_objects(obj)
