# encoding: utf-8

from OFS.interfaces import IObjectWillBeAddedEvent, IObjectWillBeRemovedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from plone import api

from . import logger
from .utility import runRelatedSearch
from .utils import add_related_roles, del_related_roles, fti_configuration, get_state


def update_security(obj, event):
    # obj.reindexObjectSecurity() seems already called: doActionFor => _invokeWithNotification() =>
    # _reindexWorkflowVariables() => reindexObjectSecurity()
    obj.reindexObjectSecurity()


def related_role_removal(obj, state, fti_config):
    if state in fti_config['static_config']:
        dic = fti_config['static_config'][state]
        uid = obj.UID()
        for princ in dic:
            if dic[princ].get('rel', ''):
                related = eval(dic[princ]['rel'])
                for utility in related:
                    if not related[utility]:
                        continue
                    for rel in runRelatedSearch(utility, obj):
                        if del_related_roles(rel, uid, princ, related[utility]):
                            rel.reindexObjectSecurity()


def related_role_addition(obj, state, fti_config):
    if state in fti_config['static_config']:
        dic = fti_config['static_config'][state]
        uid = obj.UID()
        for princ in dic:
            if dic[princ].get('rel', ''):
                related = eval(dic[princ]['rel'])
                for utility in related:
                    if not related[utility]:
                        continue
                    for rel in runRelatedSearch(utility, obj):
                        add_related_roles(rel, uid, princ, related[utility])
                        rel.reindexObjectSecurity()


def related_change_on_transition(obj, event):
    """ Set local roles on related objects after transition """
    (fti_config, fti) = fti_configuration(obj)
    if 'static_config' not in fti_config:
        return
    if event.old_state.id != event.new_state.id:  # escape creation
        # We have to remove the configuration linked to old state
        related_role_removal(obj, event.old_state.id, fti_config)
        # We have to add the configuration linked to new state
        related_role_addition(obj, event.new_state.id, fti_config)


def related_change_on_removal(obj, event):
    """ Set local roles on related objects after removal """
    (fti_config, fti) = fti_configuration(obj)
    if 'static_config' not in fti_config:
        return
    # We have to remove the configuration linked to deleted object
    # There is a problem in Plone 4.3. The event is notified before the confirmation and after too.
    # The action could be cancelled: we can't know this !! Resolved in Plone 5...
    # We choose to update related objects anyway !!
    related_role_removal(obj, get_state(obj), fti_config)


def related_change_on_addition(obj, event):
    """ Set local roles on related objects after addition """
    (fti_config, fti) = fti_configuration(obj)
    if 'static_config' not in fti_config:
        return
    related_role_addition(obj, get_state(obj), fti_config)


def related_change_on_moving(obj, event):
    """ Set local roles on related objects before moving """
    if IObjectWillBeAddedEvent.providedBy(event) or IObjectWillBeRemovedEvent.providedBy(event):  # not move
        return
    if event.oldParent and event.newParent and event.oldParent == event.newParent:  # rename
        return
    (fti_config, fti) = fti_configuration(obj)
    if 'static_config' not in fti_config:
        return
    related_role_removal(obj, get_state(obj), fti_config)


def related_change_on_moved(obj, event):
    """ Set local roles on related objects after moving """
    if IObjectAddedEvent.providedBy(event) or IObjectRemovedEvent.providedBy(event):  # not move
        return
    if event.oldParent and event.newParent and event.oldParent == event.newParent:  # rename
        return
    (fti_config, fti) = fti_configuration(obj)
    if 'static_config' not in fti_config:
        return
    related_role_addition(obj, get_state(obj), fti_config)


def configuration_change_analysis(event):
    """
        Analyses the configuration changes and returns:
         * a set of objects for which the catalog security must be updated
         * a dict for related roles to remove
         * a dict for related roles to add
    """
    def compare_lists(old, new):
        """ Compare lists and return set of common items, added items and removed items """
        old_set = set(old)
        new_set = set(new)
        return old_set & new_set, new_set - old_set, old_set - new_set

    def add_modifications(target, state, modif):
        if state not in target:
            target[state] = {}
        for princ in modif:
            if princ not in target:
                target[state][princ] = {'rel': ''}
            if modif[princ]['rel']:
                if target[state][princ]['rel'] and target[state][princ]['rel'] != modif[princ]['rel']:
                    logger.error("Related configuration to add '%s' differs '%s'" %
                                 (modif[princ]['rel'], target[state][princ]['rel']))
                target[state][princ]['rel'] = modif[princ]['rel']

    only_reindex = set()
    rem_rel_roles = {}
    add_rel_roles = {}

    # state key can be added or removed
    com_state_set, add_state_set, rem_state_set = compare_lists(event.old_value.keys(), event.new_value.keys())
    if rem_state_set:
        only_reindex |= rem_state_set
        for st in rem_state_set:
            add_modifications(rem_rel_roles, st, event.old_value[st])
    if add_state_set:
        only_reindex |= add_state_set
        for st in add_state_set:
            add_modifications(add_rel_roles, st, event.new_value[st])
    # principal can be added or removed
    for st in com_state_set:
        com_princ_set, add_princ_set, rem_princ_set = compare_lists(event.old_value[st].keys(),
                                                                    event.new_value[st].keys())
        if rem_princ_set:
            only_reindex |= set([st])
            for pr in rem_princ_set:
                add_modifications(rem_rel_roles, st, {pr: event.old_value[st][pr]})
        if add_princ_set:
            only_reindex |= set([st])
            for pr in add_princ_set:
                add_modifications(add_rel_roles, st, {pr: event.new_value[st][pr]})
        for pr in com_princ_set:
            # roles can be added or removed
            com_roles_set, add_roles_set, rem_roles_set = compare_lists(event.old_value[st][pr]['roles'],
                                                                        event.new_value[st][pr]['roles'])
            if add_roles_set or rem_roles_set:
                only_reindex |= set([st])
            # rel can be added or removed
            if event.old_value[st][pr].get('rel', '') != event.new_value[st][pr].get('rel', ''):
                if event.old_value[st][pr].get('rel', ''):
                    add_modifications(rem_rel_roles, st, {pr: event.old_value[st][pr]})
                if event.new_value[st][pr].get('rel', ''):
                    add_modifications(add_rel_roles, st, {pr: event.new_value[st][pr]})

    return only_reindex, rem_rel_roles, add_rel_roles


def local_role_related_configuration_updated(event):
    """
        Local roles configuration modification: we have to compare old and new values.
        event.old_value is like : {'private': {'raptor': {'rel': "{'dexterity.localroles.related_parent': ['Editor']}",
                                                          'roles': ('Reader',)}}}
    """
    only_reindex, rem_rel_roles, add_rel_roles = configuration_change_analysis(event)
    portal = api.portal.getSite()
    if only_reindex:
        logger.info('Objects security update')
        for brain in portal.portal_catalog(portal_type=event.fti.__name__, review_state=list(only_reindex)):
            obj = brain.getObject()
            obj.reindexObjectSecurity()
    if rem_rel_roles:
        logger.info("Removing related roles: %s" % rem_rel_roles)
        for st in rem_rel_roles:
            for brain in portal.portal_catalog(portal_type=event.fti.__name__, review_state=st):
                related_role_removal(brain.getObject(), brain.review_state, {event.field: rem_rel_roles})
    if add_rel_roles:
        logger.info('Adding related roles: %s' % add_rel_roles)
        for st in add_rel_roles:
            for brain in portal.portal_catalog(portal_type=event.fti.__name__, review_state=st):
                related_role_addition(brain.getObject(), brain.review_state, {event.field: add_rel_roles})
