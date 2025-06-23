Changelog
=========

2.0.0a1 (unreleased)
--------------------

- Added Plone 6.1 version in buildout.
  [chris-adam, sgeulette]
- Added `dexterity.localroles.related_parent_with_portal` utility to include Plone Site in related parent search.
  [sgeulette]

2.0.0a (2023-11-28)
-------------------

- Plone 4.3 and 6.0 compliant
  [sgeulette]

1.6 (2022-07-01)
----------------

- Added 'rel' (related) handling in `utils.update_roles_in_fti`
  [sgeulette]
- Added 'rem' action in `utils.update_roles_in_fti`
  [sgeulette]
- Added 'portal_type' parameter in `utils.fti_configuration`
  [sgeulette]

1.5 (2021-08-27)
----------------

- Added `update_roles_in_fti` method to update local roles in a config.
  [sgeulette]
- Added `update_security_index` method to update security index
  [sgeulette]

1.4 (2019-06-23)
----------------

- Safe dict key access
  [sgeulette]
- Added css id in configuration form.
  [sgeulette]

1.3 (2018-11-06)
----------------

- Use safely state title in unicode.
  [sgeulette]

1.2 (2017-05-30)
----------------

- Refactored utils method
  [sgeulette]
- Added method to delete related uid annotation.
  [sgeulette]

1.1 (2016-04-18)
----------------

- Useless subscriber removed.
  [sgeulette]

1.0 (2015-11-24)
----------------

- Use only local roles in vocabulary.
  [sgeulette]
- Store all configuration in one fti attribute 'localroles'.
  Useful for dexterity.localrolesfield to avoid a field name is an existing attribute
  [sgeulette]
- Add a related field to store a text configuration that will be used to set related objects local roles.
  [sgeulette]
- Add related search utility
  [sgeulette]
- Change related local roles on transition, on addition, on removal, on moving, on configuration changes
  [sgeulette]
- Add an adapter for related local roles
  [sgeulette]
- Simplify code
  [sgeulette]

0.2 (2015-06-02)
----------------

- Avoid exception on site deletion
  [sgeulette]


0.1 (2014-10-24)
----------------

- Various improvements
  [mpeeters, sgeulette]
- Added tests
  [sgeulette]
- Some improvements
  [sgeulette]
- Add validation on configuration view
  [mpeeters]
- Add localroles configuration view
  [mpeeters]
- Add an adapter for borg.localrole
  [mpeeters]
