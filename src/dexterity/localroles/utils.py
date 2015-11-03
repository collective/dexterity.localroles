# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

from Products.CMFPlone.utils import base_hasattr
from plone.dexterity.interfaces import IDexterityFTI

from . import logger


def fti_configuration(context):
    """ Return the localroles fti configuration """
    try:
        fti = getUtility(IDexterityFTI, name=context.portal_type)
    except ComponentLookupError:
        return {}
    if not base_hasattr(fti, 'localroles'):
        return {}
    return fti.localroles


def add_fti_configuration(portal_type, configuration, keyname='static_config', force=False):
    """
        Add in fti a specific localroles configuration
    """
    try:
        fti = getUtility(IDexterityFTI, name=portal_type)
    except ComponentLookupError:
        logger.error("The portal type '%s' doesn't exist" % portal_type)
        return "The portal type '%s' doesn't exist" % portal_type
    if not base_hasattr(fti, 'localroles'):
        setattr(fti, 'localroles', {})
    if keyname in fti.localroles and not force:
        logger.warn("The '%s' configuration on type '%s' is already set" % (keyname, portal_type))
        return "The '%s' configuration on type '%s' is already set" % (keyname, portal_type)
    fti.localroles[keyname] = configuration
