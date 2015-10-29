# -*- coding: utf-8 -*-
import logging

from zope.component import getUtilitiesFor

from Products.CMFPlone.utils import base_hasattr
from plone.dexterity.interfaces import IDexterityFTI

logger = logging.getLogger('dexterity.localroles: upgrade. ')


def v2(context):
    for (name, fti) in getUtilitiesFor(IDexterityFTI):
        if not base_hasattr(fti, 'localroleconfig'):
            continue
        logger.info("FTI '%s' => Copying static_config: '%s'" % (name, fti.localroleconfig))
        if not base_hasattr(fti, 'localroles'):
            setattr(fti, 'localroles', {})
        fti.localroles['static_config'] = fti.localroleconfig
        delattr(fti, 'localroleconfig')
