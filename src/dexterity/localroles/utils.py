# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.annotation.interfaces import IAnnotations

from Products.CMFPlone.utils import base_hasattr
from plone.dexterity.interfaces import IDexterityFTI

from . import logger

rel_key = 'd.lr.related'


def add_related_roles(context, uid, principal, roles):
    """ Add related roles on context for uid. """
    annot = IAnnotations(context)
    if rel_key not in annot:
        annot[rel_key] = {}
    if uid not in annot[rel_key]:
        annot[rel_key][uid] = {}
    if principal not in annot[rel_key][uid]:
        annot[rel_key][uid][principal] = set(roles)
    else:
        annot[rel_key][uid][principal] |= set(roles)


def del_related_roles(context, uid):
    """ Delete uid related roles on context """
    annot = IAnnotations(context)
    if rel_key not in annot or uid not in annot[rel_key]:
        return {}
    return annot[rel_key].pop(uid)


def get_related_roles(context, uid):
    """ Get related roles on context for uid """
    annot = IAnnotations(context)
    if rel_key not in annot or uid not in annot[rel_key]:
        return {}
    return annot[rel_key][uid]


def set_related_roles(context, uid, dic):
    """
        Set related roles on context for uid.
        Param dic is {'principal': set([roles])}
    """
    annot = IAnnotations(context)
    if rel_key not in annot:
        annot[rel_key] = {}
    annot[rel_key][uid] = dic


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
        Add in fti a specific localroles configuration.
        Param configuration is like:
        {state: {principal: {'roles': [roles], 'rel': "[{'utility': utility,'roles':[roles]}]"}}}
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
