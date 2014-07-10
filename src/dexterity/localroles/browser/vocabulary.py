# encoding: utf-8

from five import grok
from plone import api
from zope.interface import Interface
from z3c.form.interfaces import ITerms
from z3c.form.term import ChoiceTermsVocabulary
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IWidget
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from dexterity.localroles import PMF
from dexterity.localroles.browser.interfaces import IStateField


def list_2_vocabulary(elements):
    terms = []
    for item in elements:
        term = SimpleVocabulary.createTerm(item[0],
                                           item[0],
                                           item[1])
        terms.append(term)
    return SimpleVocabulary(terms)


class StateTerms(ChoiceTermsVocabulary, grok.MultiAdapter):
    grok.implements(ITerms)
    grok.adapts(Interface,
                IFormLayer,
                Interface,
                IStateField,
                IWidget)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

        portal_type = self.form.parentForm.context
        portal_workflow = portal_type.portal_workflow
        workflow = portal_workflow.getWorkflowsFor(portal_type.__name__)[0]

        self.terms = list_2_vocabulary([(s, s) for s in workflow.states])
        field.vocabulary = self.terms


@grok.provider(IContextSourceBinder)
def plone_role_generator(context):
    portal = api.portal.getSite()
    roles = []
    filtered_roles = ['Anonymous', 'Authenticated', 'Manager', 'Member', 'Site Administrator']
    for role in portal.__ac_roles__:
        if role not in filtered_roles:
            roles.append((role, PMF(role)))
    return list_2_vocabulary(sorted(roles))
