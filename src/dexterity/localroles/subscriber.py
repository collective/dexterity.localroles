# encoding: utf-8

from plone import api

from dexterity.localroles import logger


def update_security(context, event):
    context.reindexObjectSecurity()


def local_role_configuration_updated(context, event):
    """Reindex security for objects"""
    portal = api.portal.getSite()
    logger.info('Objects security update')
    for brain in portal.portal_catalog(portal_type=context.fti.__name__):
        obj = brain.getObject()
        obj.reindexObjectSecurity()
