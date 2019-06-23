Changelog
=========

1.5 (unreleased)
----------------

- Nothing changed yet.


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
