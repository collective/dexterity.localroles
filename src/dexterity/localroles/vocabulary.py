# encoding: utf-8

from five import grok
from zope.component import getUtilitiesFor
from zope.interface import Interface
from z3c.form.interfaces import ITerms
from z3c.form.term import ChoiceTermsVocabulary
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IWidget
from zope.i18n import translate
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from plone.app.workflow.interfaces import ISharingPageRole

from dexterity.localroles import PMF
from dexterity.localroles.browser.interfaces import IWorkflowState


def list_2_vocabulary(elements):
    """ Return vocabulary from list of tuples """
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
                IWorkflowState,
                IWidget)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

        portal_type = self.form.parentForm.context
        states = self.get_workflow_states(portal_type)
        self.terms = list_2_vocabulary(states)
        field.vocabulary = self.terms

    def get_workflow_states(self, portal_type):
        portal_workflow = portal_type.portal_workflow
        workflow = portal_workflow.getWorkflowsFor(portal_type.__name__)
        if not workflow:
            return []
        states = []
        for key, state in workflow[0].states.items():
            title = translate(PMF(state.title), context=self.request)
            states.append((key, title))
        return states


@grok.provider(IContextSourceBinder)
def plone_role_generator(context):
    """ Return local roles vocabulary """
    return list_2_vocabulary(sorted([(i[0], PMF(i[0])) for i in getUtilitiesFor(ISharingPageRole)]))
