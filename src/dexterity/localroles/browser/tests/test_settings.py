# encoding: utf-8

from zope.interface import Interface
from zope.schema.interfaces import IText
from z3c.form.interfaces import ITextWidget
from dexterity.localroles import testing
from dexterity.localroles.browser.exceptions import RelatedFormatError, RoleNameError, UnknownPrincipalError
from dexterity.localroles.browser import settings

import unittest


class TestSettings(unittest.TestCase):
    layer = testing.DLR_PROFILE_FUNCTIONAL

    def test_rolefield_validator(self):
        validator = settings.RoleFieldValidator(None, None, None, None, None)
        self.assertIsNone(validator.validate('foo', force=False))
        self.assertIsNone(validator.validate('admin', force=True))
        self.assertIsNone(validator.validate('Reviewers', force=True))
        self.assertRaises(UnknownPrincipalError, validator.validate, 'foo', force=True)

    def test_related_format_validator(self):
        validator = settings.RelatedFormatValidator(None, None, None, IText, ITextWidget)
        self.assertIsNone(validator.validate(' '))
        # eval exception
        self.assertRaises(RelatedFormatError, validator.validate, 'abcd')
        # test list type
        self.assertRaises(RelatedFormatError, validator.validate, '{}')
        # empty list is ok
        self.assertIsNone(validator.validate('[]'))
        # test content of list: must be a dict
        self.assertRaises(RelatedFormatError, validator.validate, "['aa']")
        # empty dic in list is ok
        self.assertIsNone(validator.validate('[{}]'))
        # test first if dict contains key 'utility'
        self.assertRaises(RelatedFormatError, validator.validate, "[{'utilityy':''}]")
        # test after if dict contains key 'roles'
        self.assertRaises(RelatedFormatError, validator.validate, "[{'utility':'','roless':[]}]")
        self.assertRaises(RelatedFormatError, validator.validate, "[{'utility':'','roles':''}]")
        # empty role list is ok
        self.assertIsNone(validator.validate("[{'utility':'','roles':[]}]"))
        # test roles
        self.assertRaises(RoleNameError, validator.validate, "[{'utility':'','roles':['ReaderR']}]")
        # all is ok
        self.assertIsNone(validator.validate("[{'utility':'','roles':['Reader']}]"))

    def test_localroleconfigurationadapter_convert(self):
        cls = settings.LocalRoleConfigurationAdapter
        values = [{'state': 'private', 'value': 'raptor',
                   'roles': ('Reader', 'Contributor'), 'related': ''},
                  {'state': 'private', 'value': 'caveman',
                   'roles': ('Reader', ), 'related': ''},
                  {'state': 'pending', 'value': 'caveman',
                   'roles': ('Contributor', ), 'related': ''}]
        dict_values = {'private': {'raptor': {'roles': ('Reader', 'Contributor'), 'rel': ''},
                                   'caveman': {'roles': ('Reader', ), 'rel': ''}},
                       'pending': {'caveman': {'roles': ('Contributor', ), 'rel': ''}}}
        self.assertEqual(dict_values, cls.convert_to_dict(values))
        self.assertItemsEqual(values, cls.convert_to_list(dict_values))
