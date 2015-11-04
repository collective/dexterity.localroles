# -*- coding: utf-8 -*-
"""Example."""
from Acquisition import aq_inner, aq_parent
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements

from .interfaces import ILocalRolesRelatedSearchUtility


class ParentRelatedSearch(object):
    """ Example related search. """

    implements(ILocalRolesRelatedSearchUtility)

    def get_objects(self, context):
        """ Return the parent. """
        return [aq_parent(aq_inner(context))]


def runRelatedSearch(utility, context):
    """ Run the related search and return the result """
    try:
        util = getUtility(ILocalRolesRelatedSearchUtility, utility)
    except ComponentLookupError:
        return []
    return util.get_objects(context)
