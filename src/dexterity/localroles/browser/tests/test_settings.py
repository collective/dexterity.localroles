# encoding: utf-8

from dexterity.localroles import testing
from dexterity.localroles.browser import exceptions
from dexterity.localroles.browser import settings

import unittest


class TestSettings(unittest.TestCase):
    layer = testing.DLR_PROFILE_FUNCTIONAL

    def test_rolefield_validator(self):
        validator = settings.RoleFieldValidator(None, None, None, None, None)
        self.assertIsNone(validator.validate('foo', force=False))
        self.assertIsNone(validator.validate('admin', force=True))
        self.assertIsNone(validator.validate('Reviewers', force=True))
        self.assertRaises(exceptions.UnknownPrincipalError,
                          validator.validate, 'foo', force=True)

    def test_localroleconfigurationadapter_convert(self):
        cls = settings.LocalRoleConfigurationAdapter
        values = [{'state': 'private', 'value': 'raptor',
                   'roles': ('Reader', 'Contributor')},
                  {'state': 'private', 'value': 'caveman',
                   'roles': ('Reader', )},
                  {'state': 'pending', 'value': 'caveman',
                   'roles': ('Contributor', )}]
        dict_values = {'private': {'raptor': ('Reader', 'Contributor'),
                                   'caveman': ('Reader', )},
                       'pending': {'caveman': ('Contributor', )}}
        self.assertEqual(dict_values, cls.convert_to_dict(values))
        self.assertItemsEqual(values, cls.convert_to_list(dict_values))
