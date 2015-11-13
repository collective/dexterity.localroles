# encoding: utf-8

from zope.schema.interfaces import IText
from z3c.form.interfaces import ITextWidget
from dexterity.localroles import testing
from ..exceptions import RelatedFormatError, RoleNameError
from ..exceptions import UnknownPrincipalError, UtilityNameError
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
        # test dict type
        self.assertRaises(RelatedFormatError, validator.validate, '[]')
        # empty dict is ok
        self.assertIsNone(validator.validate('{}'))
        # test key as utility
        self.assertRaises(UtilityNameError, validator.validate, "{'dexterity.localroles.related_parentt':[]}")
        # test value format
        self.assertRaises(RelatedFormatError, validator.validate,
                          "{'dexterity.localroles.related_parent':''}")
        # empty role list is ok
        self.assertIsNone(validator.validate("{'dexterity.localroles.related_parent':[]}"))
        # test roles
        self.assertRaises(RoleNameError, validator.validate,
                          "{'dexterity.localroles.related_parent':['ReaderR']}")
        # all is ok
        self.assertIsNone(validator.validate("{'dexterity.localroles.related_parent':['Reader']}"))

    def test_localroleconfigurationadapter(self):

        class dummy(object):
            def __init__(self, fti):
                self.fti = fti
                self.context = self

        fti = self.layer['portal'].portal_types.get('testingtype')
        dum = dummy(fti)
        cls = settings.LocalRoleConfigurationAdapter(dum)
        self.assertRaises(AttributeError, getattr, fti, 'localroles')
        self.assertRaises(AttributeError, getattr, cls, 'static_config')
        setattr(cls, 'static_config', [])
        setattr(cls, 'static_config', [{'state': 'private', 'value': 'raptor',
                                        'roles': ('Reader',), 'related': ''}])
        self.assertIsInstance(getattr(cls, 'static_config'), list)
        self.assertEqual(len(getattr(cls, 'static_config')), 1)
        self.assertDictEqual(getattr(cls, 'static_config')[0],
                             {'related': '', 'state': 'private', 'value': 'raptor', 'roles': ('Reader',)})

        values = [{'state': 'private', 'value': 'raptor',
                   'roles': ('Reader', 'Contributor'), 'related': ''},
                  {'state': 'private', 'value': 'caveman',
                   'roles': ('Reader', ), 'related': ''},
                  {'state': 'pending', 'value': 'caveman',
                   'roles': ('Contributor', ), 'related': ''}]
        dict_values = {'private': {'raptor': {'roles': ('Reader', 'Contributor'), 'rel': ''},
                                   'caveman': {'roles': ('Reader', ), 'rel': ''}},
                       'pending': {'caveman': {'roles': ('Contributor', ), 'rel': ''}}}
        self.assertDictEqual(dict_values, cls.convert_to_dict(values))
        self.assertItemsEqual(values, cls.convert_to_list(dict_values))
