# -*- coding: utf-8 -*-
from persistent.mapping import PersistentMapping
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.utils import base_hasattr
from zope.component import getUtilitiesFor

import logging


logger = logging.getLogger("dexterity.localroles: upgrade. ")


def v2(context):
    for (name, fti) in getUtilitiesFor(IDexterityFTI):
        if not base_hasattr(fti, "localroleconfig"):
            continue
        logger.info(
            "FTI '%s' => Copying static_config: '%s'" % (name, fti.localroleconfig)
        )
        if not base_hasattr(fti, "localroles"):
            setattr(fti, "localroles", PersistentMapping())
        fti.localroles["static_config"] = {}
        for state_key, state_dic in fti.localroleconfig.items():
            fti.localroles["static_config"][state_key] = {}
            for principal, roles in state_dic.items():
                fti.localroles["static_config"][state_key][principal] = {"roles": roles}
        delattr(fti, "localroleconfig")
