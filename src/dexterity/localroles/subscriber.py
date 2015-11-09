# encoding: utf-8

from plone import api

from . import logger
from .utility import runRelatedSearch
from .utils import add_related_roles, del_related_roles, fti_configuration, get_state


def update_security(obj, event):
    obj.reindexObjectSecurity()


def local_role_configuration_updated(obj, event):
    """ Reindex security for objects """
    portal = api.portal.getSite()
    logger.info('Objects security update')
    for brain in portal.portal_catalog(portal_type=obj.fti.__name__):
        obj = brain.getObject()
        obj.reindexObjectSecurity()


def related_role_removal(obj, state, fti_config):
    if state in fti_config['static_config']:
        dic = fti_config['static_config'][state]
        uid = obj.UID()
        for princ in dic:
            if dic[princ].get('rel', ''):
                related = eval(dic[princ]['rel'])
                for rel_dic in related:
                    for obj in runRelatedSearch(rel_dic['utility'], obj):
                        if del_related_roles(obj, uid):
                            obj.reindexObjectSecurity()


def related_role_addition(obj, state, fti_config):
    if state in fti_config['static_config']:
        dic = fti_config['static_config'][state]
        uid = obj.UID()
        for princ in dic:
            if dic[princ].get('rel', ''):
                related = eval(dic[princ]['rel'])
                for rel_dic in related:
                    if not rel_dic['roles']:
                        continue
                    for obj in runRelatedSearch(rel_dic['utility'], obj):
                        add_related_roles(obj, uid, princ, rel_dic['roles'])
                        obj.reindexObjectSecurity()


def related_change_on_transition(obj, event):
    """ Set local roles on related objects after transition """
    fti_config = fti_configuration(obj)
    if 'static_config' not in fti_config:
        return
    if event.old_state.id != event.new_state.id:  # escape creation
        # We have to remove the configuration linked to old state
        related_role_removal(obj, event.old_state.id, fti_config)
        # We have to add the configuration linked to new state
        related_role_addition(obj, event.new_state.id, fti_config)


def related_change_on_removal(obj, event):
    """ Set local roles on related objects after removal """
    fti_config = fti_configuration(obj)
    if 'static_config' not in fti_config:
        return
    # We have to remove the configuration linked to deleted object
    # There is a problem in Plone 4.3. The event is notified before the confirmation and after too.
    # The action could be cancelled: we can't know this !! Resolved in Plone 5...
    # We choose to update related objects anyway !!
    related_role_removal(obj, get_state(obj), fti_config)


def related_change_on_addition(obj, event):
    """ Set local roles on related objects after addition """
    fti_config = fti_configuration(obj)
    if 'static_config' not in fti_config:
        return
    related_role_addition(obj, get_state(obj), fti_config)
