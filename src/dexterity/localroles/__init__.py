# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory

import logging

_ = MessageFactory('dexterity.localroles')
PMF = MessageFactory('plone')


logger = logging.getLogger('dexterity.localroles')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
