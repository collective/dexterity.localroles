# -*- coding: utf-8 -*-
from persistent.mapping import PersistentMapping
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import base_hasattr
from plone import api
from plone.dexterity.interfaces import IDexterityFTI

from . import logger

rel_key = 'd.lr.related'


def del_related_uid(obj, uid):
    """ Delete uid related roles on obj """
    annot = IAnnotations(obj)
    if rel_key not in annot or uid not in annot[rel_key]:
        return
    del annot[rel_key][uid]
    if not annot[rel_key]:
        del annot[rel_key]


def add_related_roles(obj, uid, principal, roles):
    """ Add related roles on obj for uid. """
    annot = IAnnotations(obj)
    if not roles:
        return
    if rel_key not in annot:
        annot[rel_key] = PersistentMapping()
    if uid not in annot[rel_key]:
        annot[rel_key][uid] = PersistentMapping()
    if principal not in annot[rel_key][uid]:
        annot[rel_key][uid][principal] = set(roles)
    else:
        annot[rel_key][uid][principal] |= set(roles)


def del_related_roles(obj, uid, principal, roles):
    """ Delete uid related roles on obj """
    annot = IAnnotations(obj)
    if rel_key not in annot or uid not in annot[rel_key] or principal not in annot[rel_key][uid]:
        return set()
    ret = annot[rel_key][uid][principal] & set(roles)
    annot[rel_key][uid][principal] -= set(roles)
    # We remove the key from annotation
    if not annot[rel_key][uid][principal]:
        del annot[rel_key][uid][principal]
    if not annot[rel_key][uid]:
        del annot[rel_key][uid]
    if not annot[rel_key]:
        del annot[rel_key]
    return ret


def get_related_roles(obj, uid):
    """ Get related roles on obj for uid """
    annot = IAnnotations(obj)
    if rel_key not in annot or uid not in annot[rel_key]:
        return {}
    return dict(annot[rel_key][uid])


def get_all_related_roles(obj):
    """ Get related roles on obj """
    annot = IAnnotations(obj)
    if rel_key not in annot:
        return {}
    ret = {}
    for uid in annot[rel_key]:
        for p in annot[rel_key][uid]:
            if p not in ret:
                ret[p] = set(annot[rel_key][uid][p])
            else:
                ret[p] |= set(annot[rel_key][uid][p])
    return ret


def set_related_roles(obj, uid, dic):
    """
        Set related roles on obj for uid.
        Param dic is {'principal': set([roles])}
    """
    annot = IAnnotations(obj)
    if rel_key not in annot:
        annot[rel_key] = PersistentMapping()
    annot[rel_key][uid] = PersistentMapping(dic)


def fti_configuration(obj):
    """ Return the localroles fti configuration """
    try:
        fti = getUtility(IDexterityFTI, name=obj.portal_type)
    except ComponentLookupError:
        return ({}, None)
    if not base_hasattr(fti, 'localroles'):
        return ({}, fti)
    return (fti.localroles, fti)


def add_fti_configuration(portal_type, configuration, keyname='static_config', force=False):
    """
        Add in fti a specific localroles configuration.
        Param configuration is like:
        {state: {principal: {'roles': [roles], 'rel': "{'utility name':[roles]}"}}}
    """
    try:
        fti = getUtility(IDexterityFTI, name=portal_type)
    except ComponentLookupError:
        logger.error("The portal type '%s' doesn't exist" % portal_type)
        return "The portal type '%s' doesn't exist" % portal_type
    if not base_hasattr(fti, 'localroles'):
        setattr(fti, 'localroles', PersistentMapping())
    if keyname in fti.localroles and not force:
        logger.warn("The '%s' configuration on type '%s' is already set" % (keyname, portal_type))
        return "The '%s' configuration on type '%s' is already set" % (keyname, portal_type)
    fti.localroles[keyname] = configuration


def get_state(obj):
    """ Return the state of the current object """
    try:
        return api.content.get_state(obj=obj)
    except (WorkflowException, api.portal.CannotGetPortalError):
        return None
