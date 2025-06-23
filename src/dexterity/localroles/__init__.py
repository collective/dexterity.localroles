# -*- extra stuff goes here -*-

from plone import api
from zope.i18nmessageid import MessageFactory

import logging


_ = MessageFactory('dexterity.localroles')
PMF = MessageFactory('plone')


logger = logging.getLogger('dexterity.localroles')
HAS_PLONE_6 = int(api.env.plone_version()[0]) >= 6


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
