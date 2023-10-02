# encoding: utf-8

from dexterity.localroles import PMF
from plone.app.workflow.interfaces import ISharingPageRole
from Products.CMFPlone.utils import safe_unicode
from z3c.form.interfaces import ITerms
from z3c.form.term import ChoiceTermsVocabulary
from zope.component import getUtilitiesFor
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


def list_2_vocabulary(elements):
    """ Return vocabulary from list of tuples """
    terms = []
    for item in elements:
        term = SimpleVocabulary.createTerm(item[0],
                                           item[0],
                                           item[1])
        terms.append(term)
    return SimpleVocabulary(terms)


@implementer(ITerms)
class StateTerms(ChoiceTermsVocabulary):

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

        if hasattr(self.form, 'parentForm'):
            portal_type = self.form.parentForm.context
        else:  # this is the case in plone6 during data conversion
            portal_type = self.form.context.__name__
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
            title = translate(PMF(safe_unicode(state.title)), context=self.request)
            states.append((key, title))
        return states


@implementer(IVocabularyFactory)
class SharingRolesVocabulary(object):
    """ Return local roles vocabulary """

    def __call__(self, context):
        return list_2_vocabulary(sorted([(i[0], PMF(i[0])) for i in getUtilitiesFor(ISharingPageRole)]))
