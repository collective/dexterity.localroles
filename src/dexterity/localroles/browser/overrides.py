# encoding: utf-8

from plone.app.dexterity.browser.layout import TypeFormLayout
from plone.app.dexterity.browser.behaviors import TypeBehaviorsPage
from plone.app.dexterity.browser.overview import TypeOverviewPage
from plone.app.dexterity.browser.fields import TypeFieldsPage

from dexterity.localroles import _


class CustomTypeFormLayout(TypeFormLayout):

    @property
    def tabs(self):
        current_tabs = super(CustomTypeFormLayout, self).tabs
        return current_tabs + ((_(u'Local roles'), '@@localroles'), )


class CustomTypeBehaviorsPage(TypeBehaviorsPage, CustomTypeFormLayout):
    pass


class CustomTypeOverviewPage(TypeOverviewPage, CustomTypeFormLayout):
    pass


class CustomTypeFieldsPage(TypeFieldsPage, CustomTypeFormLayout):
    pass
