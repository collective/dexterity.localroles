# encoding: utf-8

from dexterity.localroles import testing
from dexterity.localroles import vocabulary

import unittest


class TestVocabulary(unittest.TestCase):
    layer = testing.DLR_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']

    def test_list_2_vocabulary(self):
        elements = [(u'a', u'b'), (u'1', u'2')]
        voc = vocabulary.list_2_vocabulary(elements)
        for idx, term in enumerate(voc):
            self.assertEqual(elements[idx][0], term.value)
            self.assertEqual(elements[idx][1], term.title)

    def test_state_terms(self):
        parent_form = type('parent_form', (object, ), {})()
        parent_form.context = self.portal.portal_types.get('testingtype')
        form = type('form', (object, ), {'parentForm': parent_form})()
        field = type('field', (object, ), {'vocabulary': None})()

        state_terms = vocabulary.StateTerms(None, None, form, field, None)
        states = ['pending', 'private', 'published']
        self.assertListEqual(states, [t.value for t in state_terms.terms])

    def test_state_terms_without_workflow(self):
        parent_form = type('parent_form', (object, ), {})()
        parent_form.context = self.portal.portal_types.get('Document')
        form = type('form', (object, ), {'parentForm': parent_form})()
        field = type('field', (object, ), {'vocabulary': None})()

        state_terms = vocabulary.StateTerms(None, None, form, field, None)
        self.assertEqual([], [t for t in state_terms.terms])

    def test_plone_role_generator(self):
        voc = vocabulary.plone_role_generator(None)
        roles = [u'Contributor', u'Editor', u'Reader', u'Reviewer']
        self.assertListEqual(roles, [t.value for t in voc])
